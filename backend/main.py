"""ReviewLens AI REST API.

Run with:
    uvicorn backend.main:app --reload
"""
from backend.database import init_database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.analyze import router as analyze_router
from backend.api.dashboard import router as dashboard_router
from backend.api.reviews import router as reviews_router
from backend.api.validation import router as validation_router

app = FastAPI(
    
    title="ReviewLens AI API",
    description="AI-powered customer review intelligence backend",
    version="1.0.0",
)
init_database()

# For local hackathon development. In deployment, replace '*' with the
# actual frontend origin(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(reviews_router, prefix="/api")
app.include_router(validation_router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "ReviewLens AI",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {"status": "healthy"}
