# 🚀 Deployment Checklist

## Pre-Deployment

- [ ] All code committed to GitHub
- [ ] .env.example created (no secrets!)
- [ ] README.md complete
- [ ] Demo video recorded and uploaded
- [ ] HuggingFace models uploaded

## Backend Deployment (Railway)

- [ ] Create Railway account
- [ ] Connect GitHub repository
- [ ] Add environment variables:
  - QIANFAN_AK
  - QIANFAN_SK
  - DATABASE_URL (auto-generated)
- [ ] Deploy
- [ ] Test /api/health endpoint
- [ ] Note backend URL

## Frontend Deployment (GitHub Pages)

- [ ] Update vite.config.js with correct base path
- [ ] Update API URL in frontend code
- [ ] Run: `npm run deploy`
- [ ] Enable GitHub Pages in repo settings
- [ ] Test deployment

## Testing

- [ ] Upload test document
- [ ] Verify OCR extraction
- [ ] Check ERNIE analysis
- [ ] Test Q&A feature
- [ ] Test comparison
- [ ] Verify real-time news (if enabled)

## Submission

### CodeCraze Hackathon
- [ ] Submit GitHub repository URL
- [ ] Submit live demo URL
- [ ] Submit demo video URL
- [ ] Fill project description

### ERNIE Challenge
- [ ] Submit GitHub repository URL
- [ ] Submit HuggingFace model URLs
- [ ] Submit demo video URL
- [ ] Fill technical documentation

## Post-Deployment

- [ ] Monitor logs for errors
- [ ] Test on mobile devices
- [ ] Get user feedback
- [ ] Update README with any fixes

---

**Congratulations! You're ready to win! 🏆**