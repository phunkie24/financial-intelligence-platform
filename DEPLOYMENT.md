# 🚀 Quick Deployment Guide

## Deploy Everything from GitHub (Free & Easy)

### ✅ **Backend: Render.com (Auto-deploys from GitHub)**

1. **Sign up**: https://render.com (use your GitHub account)
2. **New Web Service** → Connect `phunkie24/financial-intelligence-platform`
3. **Configure**:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11
4. **Add Environment Variables**:
   ```
   QIANFAN_AK=your_baidu_key
   QIANFAN_SK=your_baidu_secret
   ```
5. **Deploy** → Render auto-builds from your GitHub repo!

**Result**: Get URL like `https://your-app.onrender.com`

---

### ✅ **Frontend: Vercel (Auto-deploys from GitHub)**

1. **Sign up**: https://vercel.com (use your GitHub account)
2. **Import Project** → Select `phunkie24/financial-intelligence-platform`
3. **Configure**:
   - **Framework**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. **Add Environment Variable**:
   ```
   VITE_API_URL=https://your-app.onrender.com
   ```
5. **Deploy** → Vercel auto-builds from GitHub!

**Result**: Get URL like `https://your-app.vercel.app`

---

## 🎯 **Done!**

Every time you push to GitHub:
- ✅ Render automatically rebuilds backend
- ✅ Vercel automatically rebuilds frontend
- ✅ Both are FREE

**Show judges**:
- Live Frontend: `https://your-app.vercel.app`
- Live Backend API: `https://your-app.onrender.com/docs`
- Agent Status: `https://your-app.onrender.com/api/agents/status`
