# 🚀 Render Deployment Guide for RAG System

## 📋 **Prerequisites**
- GitHub account (✅ You have this)
- Render account (free)
- Your code pushed to GitHub (✅ Done)

## 🔗 **Step 1: Create Render Account**
1. Go to [render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with your GitHub account
4. Authorize Render to access your repositories

## 🎯 **Step 2: Deploy Your RAG System**

### **Option A: Quick Deploy (Recommended)**
1. In Render dashboard, click **"New +"**
2. Select **"Web Service"**
3. Connect your GitHub repository:
   - Repository: `Manan23-dev/vector-similarity-search-for-Document-Retrieval`
   - Branch: `feature/rag-system-implementation`
4. Configure the service:
   - **Name**: `rag-search-system` (or your preferred name)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click **"Create Web Service"**

### **Option B: Manual Configuration**
If you prefer manual setup:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Python Version**: `3.9.18` (from runtime.txt)

## ⚙️ **Step 3: Environment Variables (Optional)**
If you need any environment variables:
1. Go to your service dashboard
2. Click **"Environment"** tab
3. Add any required variables

## 🚀 **Step 4: Deploy**
1. Click **"Deploy"** or **"Manual Deploy"**
2. Wait for build to complete (5-10 minutes)
3. Your service will be available at: `https://your-app-name.onrender.com`

## 🔍 **Step 5: Test Your Deployment**
Once deployed, test these endpoints:
```bash
# Health check
curl https://your-app-name.onrender.com/health

# Search API
curl -X POST https://your-app-name.onrender.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 3}'

# Q&A API
curl -X POST https://your-app-name.onrender.com/api/qa \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "top_k": 3}'
```

## 📊 **Step 6: Update Frontend**
Once you have your Render URL, update the frontend:
1. Open `docs/assets/js/demo.js`
2. Replace `BASE_URL` with your Render URL:
   ```javascript
   BASE_URL: 'https://your-app-name.onrender.com'
   ```

## 💡 **Render Free Tier Details**
- **750 hours/month** - More than enough for personal use
- **Sleeps after 15min** - Wakes up when accessed (takes ~30 seconds)
- **512MB RAM** - Sufficient for your RAG system
- **No credit card required** - Completely free

## 🆘 **Troubleshooting**

### **Build Fails**
- Check the build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### **App Crashes**
- Check the service logs
- Ensure `main.py` is the correct entry point
- Verify all imports are working

### **Slow Startup**
- Normal for free tier (sleeps after inactivity)
- First request after sleep takes ~30 seconds
- Subsequent requests are fast

## 🎉 **Success!**
Once deployed, you'll have:
- ✅ **Live RAG API** at your Render URL
- ✅ **75 training documents** indexed
- ✅ **Search and Q&A endpoints** working
- ✅ **Frontend** ready to connect

## 🔄 **Auto-Deployments**
Render automatically redeploys when you push to your GitHub branch!

---

**Need help?** Check Render's documentation or contact support - they're very helpful!
