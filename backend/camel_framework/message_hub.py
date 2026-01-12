# Databricks notebook source
"""
Agent Message Hub - Central communication router for multi-agent system.

Implements pub/sub and direct messaging patterns for agent-to-agent communication.
Uses CAMEL's BaseMessage format for standardized message passing.

Features:
- Direct agent-to-agent messaging
- Topic-based pub/sub subscriptions
- Broadcast to multiple agents
- Message history and logging
- Async message delivery
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
from datetime import datetime

try:
    from camel.messages import BaseMessage
    from camel.types import RoleType
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    # Fallback
    class BaseMessage:
        def __init__(self, **kwargs):
            self.content = kwargs.get('content', '')
            self.meta_dict = kwargs.get('meta_dict', {})


logger = logging.getLogger(__name__)


class AgentMessageHub:
    """
    Central message routing hub for agent-to-agent communication.

    Provides three communication patterns:
    1. Direct messaging: Agent A → Agent B
    2. Pub/Sub: Agents subscribe to topics and receive published messages
    3. Broadcast: Send message to multiple agents simultaneously

    Example Usage:
        hub = AgentMessageHub()
        hub.register_agent("Financial Analyst", financial_analyst)
        hub.register_agent("Risk Assessor", risk_assessor)

        # Direct message
        response = await hub.send_direct(
            from_agent="Financial Analyst",
            to_agent="Risk Assessor",
            message=BaseMessage(content="Analysis complete")
        )

        # Pub/Sub
        hub.subscribe("risk_alerts", risk_assessor.handle_alert)
        await hub.publish("risk_alerts", BaseMessage(content="High risk detected"))

        # Broadcast
        await hub.broadcast(
            from_agent="Orchestrator",
            message=BaseMessage(content="New task available"),
            recipients=["Financial Analyst", "Risk Assessor"]
        )
    """

    def __init__(self):
        """Initialize message hub."""
        self.agents: Dict[str, Any] = {}
        self.subscriptions: Dict[str, List[Callable]] = defaultdict(list)
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[Dict] = []
        self.max_history = 1000

        logger.info("📬 Agent Message Hub initialized")

    def register_agent(self, agent_name: str, agent: Any):
        """
        Register an agent with the hub.

        Args:
            agent_name: Unique agent identifier
            agent: Agent instance
        """
        if agent_name in self.agents:
            logger.warning(f"⚠️ Agent {agent_name} already registered. Overwriting.")

        self.agents[agent_name] = agent
        logger.info(f"✅ Agent registered: {agent_name}")

    def unregister_agent(self, agent_name: str):
        """
        Remove agent from hub.

        Args:
            agent_name: Agent to remove
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"🗑️ Agent unregistered: {agent_name}")

    def subscribe(self, topic: str, callback: Callable):
        """
        Subscribe to a topic.

        Args:
            topic: Topic name (e.g., "risk_alerts", "document_processed")
            callback: Async callback function to receive messages
        """
        self.subscriptions[topic].append(callback)
        logger.info(f"📝 Subscription added to topic '{topic}'")

    def unsubscribe(self, topic: str, callback: Callable):
        """
        Unsubscribe from a topic.

        Args:
            topic: Topic name
            callback: Callback to remove
        """
        if topic in self.subscriptions:
            try:
                self.subscriptions[topic].remove(callback)
                logger.info(f"🗑️ Unsubscribed from topic '{topic}'")
            except ValueError:
                logger.warning(f"⚠️ Callback not found in topic '{topic}'")

    async def send_direct(
        self,
        from_agent: str,
        to_agent: str,
        message: BaseMessage
    ) -> Optional[Any]:
        """
        Send message directly from one agent to another.

        Args:
            from_agent: Sender agent name
            to_agent: Recipient agent name
            message: BaseMessage to send

        Returns:
            Response from target agent (if available)

        Raises:
            ValueError: If target agent not registered
        """
        if to_agent not in self.agents:
            raise ValueError(f"❌ Agent '{to_agent}' not registered in hub")

        # Add routing metadata
        if not hasattr(message, 'meta_dict'):
            message.meta_dict = {}

        message.meta_dict.update({
            'from_agent': from_agent,
            'to_agent': to_agent,
            'timestamp': datetime.now().isoformat(),
            'message_type': 'direct'
        })

        # Store in history
        self._add_to_history(message)

        logger.info(f"📤 Direct message: {from_agent} → {to_agent}")
        logger.debug(f"Message content: {message.content[:100]}...")

        # Deliver message to target agent
        target_agent = self.agents[to_agent]

        try:
            # Check if agent has a step method (CAMEL agents)
            if hasattr(target_agent, 'step'):
                response = await target_agent.step(message)
                logger.info(f"✅ Message delivered to {to_agent}")
                return response
            else:
                logger.warning(f"⚠️ Agent {to_agent} doesn't support message handling")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to deliver message to {to_agent}: {e}")
            raise

    async def publish(self, topic: str, message: BaseMessage):
        """
        Publish message to all subscribers of a topic.

        Args:
            topic: Topic name
            message: Message to publish
        """
        if not hasattr(message, 'meta_dict'):
            message.meta_dict = {}

        message.meta_dict.update({
            'topic': topic,
            'timestamp': datetime.now().isoformat(),
            'message_type': 'pubsub'
        })

        # Store in history
        self._add_to_history(message)

        callbacks = self.subscriptions.get(topic, [])

        if not callbacks:
            logger.warning(f"⚠️ No subscribers for topic '{topic}'")
            return

        logger.info(f"📢 Publishing to topic '{topic}' ({len(callbacks)} subscribers)")

        # Call all subscriber callbacks
        results = await asyncio.gather(
            *[callback(message) for callback in callbacks],
            return_exceptions=True
        )

        # Log any errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Subscriber {i} failed: {result}")

    async def broadcast(
        self,
        from_agent: str,
        message: BaseMessage,
        recipients: Optional[List[str]] = None
    ) -> List[Any]:
        """
        Broadcast message to multiple agents.

        Args:
            from_agent: Sender agent name
            message: Message to broadcast
            recipients: List of recipient agent names (None = all agents except sender)

        Returns:
            List of responses from recipient agents
        """
        # Determine recipients
        if recipients is None:
            targets = [name for name in self.agents.keys() if name != from_agent]
        else:
            targets = recipients

        if not targets:
            logger.warning(f"⚠️ No targets for broadcast from {from_agent}")
            return []

        logger.info(f"📣 Broadcasting from {from_agent} to {len(targets)} agents")

        # Send to all targets in parallel
        tasks = [
            self.send_direct(from_agent, target, message)
            for target in targets
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any errors
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"❌ Broadcast to {targets[i]} failed: {response}")

        return responses

    def _add_to_history(self, message: BaseMessage):
        """
        Add message to history.

        Args:
            message: Message to store
        """
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'content': message.content if hasattr(message, 'content') else str(message),
            'metadata': message.meta_dict if hasattr(message, 'meta_dict') else {}
        }

        self.message_history.append(history_entry)

        # Trim history if too long
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]

    def get_conversation_history(
        self,
        agent_name: Optional[str] = None,
        topic: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get conversation history with filtering.

        Args:
            agent_name: Filter by agent (as sender or receiver)
            topic: Filter by topic
            limit: Maximum number of messages to return

        Returns:
            List of message history dictionaries
        """
        filtered = self.message_history

        if agent_name:
            filtered = [
                msg for msg in filtered
                if (msg.get('metadata', {}).get('from_agent') == agent_name or
                    msg.get('metadata', {}).get('to_agent') == agent_name)
            ]

        if topic:
            filtered = [
                msg for msg in filtered
                if msg.get('metadata', {}).get('topic') == topic
            ]

        return filtered[-limit:]

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all registered agents.

        Returns:
            Dictionary mapping agent names to their status
        """
        status = {}

        for name, agent in self.agents.items():
            if hasattr(agent, 'get_status'):
                status[name] = agent.get_status()
            else:
                status[name] = {'name': name, 'status': 'unknown'}

        return status

    def get_hub_stats(self) -> Dict[str, Any]:
        """
        Get message hub statistics.

        Returns:
            Hub statistics dictionary
        """
        return {
            'total_agents': len(self.agents),
            'registered_agents': list(self.agents.keys()),
            'total_topics': len(self.subscriptions),
            'topics': {
                topic: len(callbacks)
                for topic, callbacks in self.subscriptions.items()
            },
            'message_history_size': len(self.message_history),
            'max_history': self.max_history
        }

    async def clear_history(self):
        """Clear message history."""
        self.message_history.clear()
        logger.info("🗑️ Message history cleared")

    def __repr__(self) -> str:
        return f"<AgentMessageHub(agents={len(self.agents)}, topics={len(self.subscriptions)})>"


# COMMAND ----------

