# Databricks notebook source
"""
Optimized Prompt Templates for Financial Analysis
"""

class FinancialPrompts:
    
    RISK_ANALYSIS = """You are a financial risk analyst. Analyze the following document for risks.

Document:
{document}

Provide a structured JSON analysis:
{{
    "risk_level": "HIGH/MEDIUM/LOW",
    "risk_score": 0-100,
    "key_risks": [
        {{"risk": "description", "severity": "HIGH/MEDIUM/LOW", "category": "operational/financial/market/regulatory"}}
    ],
    "risk_categories": {{
        "operational": 0-100,
        "financial": 0-100,
        "market": 0-100,
        "regulatory": 0-100
    }},
    "mitigation": ["suggestion 1", "suggestion 2"]
}}

Analysis:"""

    SENTIMENT_ANALYSIS = """Analyze the sentiment of this financial document.

Document:
{document}

Return JSON:
{{
    "overall_sentiment": "positive/negative/neutral",
    "sentiment_score": -1.0 to 1.0,
    "confidence": 0.0 to 1.0,
    "positive_factors": ["factor 1", "factor 2"],
    "concerns": ["concern 1", "concern 2"],
    "tone": "optimistic/cautious/pessimistic/neutral",
    "recommendation": "BUY/HOLD/SELL",
    "reasoning": "explanation"
}}

Analysis:"""

    EXECUTIVE_SUMMARY = """Create a concise executive summary of this financial report.

Report:
{document}

Provide 150-200 word summary covering:
- Key Highlights (3-5 points)
- Financial Performance (revenue, profit, growth)
- Strategic Initiatives
- Outlook & Guidance
- Investor Takeaways

Summary:"""

    KEY_METRICS = """Extract key financial metrics from this document and return as JSON.

Document:
{document}

Return JSON:
{{
    "revenue": {{"value": "$X.XB", "change": "+X%", "period": "QX 2024"}},
    "profit": {{"value": "$X.XB", "change": "+X%", "period": "QX 2024"}},
    "eps": {{"value": "$X.XX", "change": "+X%"}},
    "guidance": {{
        "revenue": "range or figure",
        "profit": "range or figure",
        "outlook": "positive/negative/stable"
    }},
    "debt": {{"total": "$XB", "debt_to_equity": X.X}},
    "cash": {{"total": "$XB", "cash_flow": "$XB"}},
    "margins": {{
        "gross": "XX%",
        "operating": "XX%",
        "net": "XX%"
    }},
    "key_metrics": {{
        "metric_name": "value"
    }}
}}

Metrics:"""

    COMPARE_DOCUMENTS = """Compare these financial documents from different companies.

Company 1: {company1}
{doc1}

Company 2: {company2}
{doc2}

Provide comparison:
{{
    "winner": "company1/company2/tie",
    "financial_performance": {{
        "revenue_growth": "comparison",
        "profitability": "comparison",
        "margins": "comparison"
    }},
    "strengths": {{
        "company1": ["strength 1", "strength 2"],
        "company2": ["strength 1", "strength 2"]
    }},
    "weaknesses": {{
        "company1": ["weakness 1"],
        "company2": ["weakness 1"]
    }},
    "risk_comparison": "which is riskier and why",
    "investment_recommendation": "which to invest in and why"
}}

Comparison:"""

    QA_TEMPLATE = """Answer the question based on the financial document context provided.

Context:
{context}

Question: {question}

Provide detailed answer with:
- Direct answer to the question
- Supporting evidence from the document with specific numbers/metrics
- Confidence level (High/Medium/Low)
- Any caveats or limitations

Answer:"""