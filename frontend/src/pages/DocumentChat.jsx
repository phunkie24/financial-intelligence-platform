import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'

export default function DocumentChat() {
  const { documentId } = useParams()
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [sending, setSending] = useState(false)
  const [document, setDocument] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    loadDocument()
    loadHistory()
  }, [documentId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadDocument = async () => {
    try {
      const response = await axios.get(`/api/documents/${documentId}/analysis`)
      if (response.data.success) {
        setDocument(response.data.document)
      }
    } catch (error) {
      console.error('Load document error:', error)
    }
  }

  const loadHistory = async () => {
    // Load Q&A history if available
    // For now, start with welcome message
    setMessages([{
      type: 'assistant',
      content: 'Hello! I\'m your AI assistant. Ask me anything about this financial document.',
      timestamp: new Date()
    }])
  }

  const handleSend = async () => {
    if (!inputValue.trim() || sending) return

    const userMessage = {
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setSending(true)

    try {
      const response = await axios.post(`/api/documents/${documentId}/ask`, {
        question: inputValue
      })

      if (response.data.success) {
        const assistantMessage = {
          type: 'assistant',
          content: response.data.answer,
          sources: response.data.sources,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, assistantMessage])
      }
    } catch (error) {
      console.error('Q&A error:', error)
      const errorMessage = {
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your question. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setSending(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 h-screen flex flex-col">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold" style={{ color: 'var(--primary)' }}>
          💬 Document Q&A
        </h1>
        {document && (
          <p className="text-sm text-gray-600 mt-1">
            Chatting about: {document.filename}
          </p>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto bg-white rounded-lg shadow p-6 mb-4">
        <div className="space-y-4">
          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-300">
                    <p className="text-xs font-semibold mb-1">Sources:</p>
                    {message.sources.map((source, sidx) => (
                      <p key={sidx} className="text-xs opacity-75">
                        • Chunk {source.chunk_id} (relevance: {(source.relevance * 100).toFixed(0)}%)
                      </p>
                    ))}
                  </div>
                )}
                
                <p className="text-xs mt-2 opacity-75">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {sending && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg p-4">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex gap-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about this document..."
            className="flex-1 px-4 py-2 border rounded-lg resize-none focus:outline-none focus:ring-2"
            style={{ borderColor: '#E2E8F0' }}
            rows="2"
            disabled={sending}
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || sending}
            className="px-6 py-2 rounded-lg font-semibold text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ backgroundColor: 'var(--primary)' }}
          >
            {sending ? '⏳' : '📤'} Send
          </button>
        </div>
        
        <div className="mt-2 flex gap-2 flex-wrap">
          <button
            onClick={() => setInputValue("What are the key financial metrics?")}
            className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full"
            disabled={sending}
          >
            💰 Key Metrics
          </button>
          <button
            onClick={() => setInputValue("What are the main risks mentioned?")}
            className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full"
            disabled={sending}
          >
            ⚠️ Risks
          </button>
          <button
            onClick={() => setInputValue("Summarize the outlook and guidance")}
            className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full"
            disabled={sending}
          >
            🔮 Outlook
          </button>
        </div>
      </div>
    </div>
  )
}