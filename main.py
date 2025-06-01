import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Your existing imports here

app = FastAPI(
    title="Vector Similarity Search API",
    description="A high-performance document retrieval system using HNSWlib and FastAPI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Vector Similarity Search API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Your existing routes here

# Important for Vercel
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
