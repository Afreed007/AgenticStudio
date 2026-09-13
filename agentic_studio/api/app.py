"""FastAPI application initialization."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(
    title="Agentic Studio API",
    description="Backend API and WebSocket Gateway for the Autonomous Multi-Agent Software Factory",
    version="0.1.0",
)

# Enable CORS for Angular frontend (localhost:4200) and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API and WebSocket routes
app.include_router(router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Agentic Studio API"}
