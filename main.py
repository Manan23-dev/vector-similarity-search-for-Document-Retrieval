from fastapi import FastAPI
from src.api.endpoints import router

app = FastAPI()

# Include the API router
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Vector Similarity Search API is running!"}
