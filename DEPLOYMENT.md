# Vercel Deployment Guide for RAG System

## 🚀 Quick Deployment Steps

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy from Project Directory
```bash
cd /Users/mananpatel/Desktop/Projects/vector-similarity-search-for-Document-Retrieval
vercel
```

### 4. Follow the Prompts
- **Set up and deploy?** → Yes
- **Which scope?** → Your account
- **Link to existing project?** → No
- **What's your project's name?** → `rag-vector-search` (or your preferred name)
- **In which directory is your code located?** → `./` (current directory)

### 5. Environment Variables (Optional)
If you need any environment variables, add them in the Vercel dashboard or via CLI:
```bash
vercel env add VARIABLE_NAME
```

## 📁 Project Structure for Vercel

```
├── main.py                 # FastAPI app (entry point)
├── vercel.json            # Vercel configuration
├── requirements-vercel.txt # Python dependencies
├── .vercelignore          # Files to ignore
├── src/                   # Your source code
│   ├── api/
│   ├── embeddings/
│   └── index/
└── example_data/          # Training data
```

## 🔧 Configuration Details

### vercel.json
- Uses `@vercel/python` builder
- Routes all requests to `main.py`
- Sets Python 3.9 as the runtime

### requirements-vercel.txt
- Simplified dependencies without version constraints
- Optimized for Vercel's build environment

### .vercelignore
- Excludes frontend, tests, and development files
- Keeps deployment lightweight

## 🌐 After Deployment

1. **Get your deployment URL** from Vercel dashboard
2. **Update frontend** to use the new backend URL
3. **Test the API** endpoints

## 🔍 Testing Your Deployment

```bash
# Test health endpoint
curl https://your-app.vercel.app/health

# Test search endpoint
curl -X POST https://your-app.vercel.app/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 3}'

# Test QA endpoint
curl -X POST https://your-app.vercel.app/api/qa \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "top_k": 3}'
```

## 🚨 Important Notes

- **Cold Starts**: First request may be slower due to model loading
- **Memory Limits**: Vercel has memory limits for serverless functions
- **Timeout**: Functions have execution time limits
- **File System**: Use `/tmp` for temporary files if needed

## 🔄 Updating Deployment

To update your deployment:
```bash
vercel --prod
```

## 📊 Monitoring

- Check Vercel dashboard for logs and metrics
- Monitor function execution times
- Watch for memory usage spikes

## 🆘 Troubleshooting

### Common Issues:
1. **Import Errors**: Check Python path and dependencies
2. **Memory Issues**: Optimize model loading
3. **Timeout**: Reduce model complexity or use caching
4. **CORS**: Already handled in your FastAPI app

### Debug Commands:
```bash
# View logs
vercel logs

# Check function details
vercel inspect

# Test locally
vercel dev
```
