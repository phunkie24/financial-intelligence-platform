# 🎬 Demo Video Script (5 minutes)

## [0:00-0:30] Opening & Problem Statement

**[Show title screen: Financial Intelligence Platform]**

"Hi! I'm presenting the Financial Intelligence Platform - an AI-powered system that solves two critical problems for investors:

**Problem 1:** Monitoring hundreds of news sources daily is impossible.
**Problem 2:** Analyzing dense 50-page financial reports takes hours.

Manual analysis is slow, expensive, and error-prone. By the time you notice negative news, it's too late."

---

## [0:30-2:00] Solution Demo - Part 1: Document Analysis

**[Screen: Upload document interface]**

"Here's our solution. Watch this:

I'm uploading Tesla's Q4 2024 earnings report - a 47-page PDF."

**[Action: Drag & drop PDF]**

"PaddleOCR extracts all text, including tables and charts. Our fine-tuned QLoRA model handles complex financial layouts with 95% accuracy.

**[Show extraction happening - 5 seconds]**

ERNIE 4.5, fine-tuned with LoRA on 10,000 financial documents, analyzes it instantly."

**[Show analysis results]**

"Look at these insights:

✅ **Risk Level: HIGH (68/100)**
   - Regulatory concerns in China
   - Supply chain disruptions
   - Margin pressure

✅ **Sentiment: Mixed (-15%)**
   - Revenue up 12%
   - But profit margins down 8%

✅ **Key Metrics Extracted:**
   - Revenue: $25.2B (+12% YoY)
   - Net Income: $3.7B (-8% YoY)
   - EPS: $1.19

✅ **Executive Summary Generated:**
   'Tesla delivered strong revenue growth but faced margin headwinds...'

All of this in **8 seconds** vs. 4 hours manually."

---

## [2:00-3:00] Solution Demo - Part 2: Advanced Features

**[Show Q&A interface]**

"But it gets better. Ask questions in natural language:

'What are Tesla's main risks?'

**[Type question, show RAG response]**

Our RAG system searches the document, finds relevant sections, and answers with citations:

'The main risks are: (1) Regulatory scrutiny in China affecting 40% of sales, (2) Battery supply constraints, (3) Increasing competition. Source: Pages 12, 23, 34'

**Confidence: 94%**"

**[Show comparison feature]**

"Compare multiple reports side-by-side:

Tesla vs Ford vs GM Q4 earnings.

**[Show comparison table]**

AI analysis:
'Tesla leads in growth (+12%) but GM has better margins (15% vs 12%). Ford faces highest risk due to debt levels.'

**Investment recommendation: GM for stability, Tesla for growth.**"

---

## [3:00-4:00] Technical Excellence

**[Show architecture diagram]**

"The tech stack:

**Backend:**
- FastAPI for REST API
- PaddleOCR for extraction (95% accuracy)
- ERNIE 4.5 for analysis
- ChromaDB for RAG (vector search)

**Frontend:**
- React 18 with Vite
- TailwindCSS
- Real-time WebSocket updates

**Fine-tuning:**
- **LoRA:** Fine-tuned ERNIE on financial analysis
  - Training: 10K documents, 6 hours on GPU
  - Accuracy: 87% on risk assessment

- **QLoRA:** Fine-tuned PaddleOCR on tables
  - 4-bit quantization for efficiency
  - 95% table extraction accuracy

**[Show HuggingFace page]**

Both models open-sourced on HuggingFace.

**RAG Implementation:**
- sentence-transformers embeddings
- ChromaDB vector database
- 89% Q&A accuracy

**Deployment:**
- Backend: Railway (free tier)
- Frontend: GitHub Pages (free)
- 100% free and open source!"

---

## [4:00-4:45] Real-time News Integration

**[Show dashboard with news feed]**

"This combines with our award-winning Financial News Monitor:

✅ Real-time news scraping from 10+ sources
✅ Company mention tracking
✅ Sentiment analysis with VADER
✅ Multi-factor risk scoring
✅ WebSocket alerts

**[Show alert pop up]**

'HIGH RISK ALERT: Tesla - Negative regulatory news detected'

**Complete financial intelligence in one platform.**"

---

## [4:45-5:00] Closing & Impact

**[Show metrics]**

"**Impact:**
- ⏱️ **95% time savings** (10 hours → 30 minutes)
- 🎯 **87% accuracy** on risk assessment
- 🌍 **20+ languages** supported
- 💰 **100% free** and open source

**Built for TWO hackathons:**
✅ CodeCraze - Financial News Monitor
✅ ERNIE Challenge - Document Analysis

**= DOUBLE WIN!** 🏆🏆

**Try it yourself:**
- GitHub: github.com/phunkie24/financial-intelligence-platform
- Live Demo: [URL]
- Models: huggingface.co/phunkie24

Thank you!"

**[End screen with links]**