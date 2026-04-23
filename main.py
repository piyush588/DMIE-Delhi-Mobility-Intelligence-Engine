import uvicorn
from fastapi import FastAPI
from app.api.routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import db

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Attempt to connect to MongoDB
    try:
        await db.connect()
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
    yield
    # Shutdown: Disconnect from MongoDB
    await db.disconnect()

app = FastAPI(
    title="Delhi Mobility Intelligence Engine (DMIE)",
    description="V1 MVP - Smart Route mode comparison with Peak Hour & Metro Intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to DMIE API",
        "docs": "/docs",
        "endpoints": {
            "recommend": "/api/v1/recommend",
            "health": "/api/v1/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
