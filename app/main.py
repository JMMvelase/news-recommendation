from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import time
import os
import logging

load_dotenv()

from app.recommender import NewsRecommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="News Recommendation API",
    description="Semantic news recommendation using Sentence Transformers and FAISS",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

recommender = None
load_error = None


@app.on_event("startup")
def load_recommender():
    global recommender, load_error
    try:
        logger.info("Loading recommender...")
        recommender = NewsRecommender(
            index_path=os.getenv("FAISS_INDEX_PATH", "data/news_rec_embeddings.faiss"),
            articles_path=os.getenv("ARTICLES_PATH", "data/news_articles.parquet"),
            model_name=os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"),
        )
        logger.info("Recommender loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load recommender: {e}")
        load_error = str(e)


# --- Request / Response Models ---


class RecommendationRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    k: int = Field(default=int(os.getenv("TOP_K", "5")), ge=1, le=20)


class ArticleResult(BaseModel):
    headline: str
    category: str
    similarity: float
    link: str


class RecommendationResponse(BaseModel):
    query: str
    recommendations: list[ArticleResult]
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    articles: int | None = None
    vectors: int | None = None
    error: str | None = None


# --- Routes ---


@app.get("/health", response_model=HealthResponse)
def health():
    if load_error:
        return HealthResponse(status="unhealthy", error=load_error)
    if recommender is None:
        return HealthResponse(status="loading")
    return HealthResponse(
        status="healthy",
        articles=len(recommender.articles),
        vectors=recommender.index.ntotal,
    )


@app.post("/recommend", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest):
    if recommender is None:
        raise HTTPException(
            status_code=503,
            detail="Recommender not loaded. Check /health for details.",
        )

    start_time = time.perf_counter()

    try:
        results = recommender.recommend(request.query, request.k)
    except Exception as e:
        logger.error(f"Recommendation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Recommendation failed. Please try again.",
        )

    latency_ms = (time.perf_counter() - start_time) * 1000

    return RecommendationResponse(
        query=request.query,
        recommendations=[ArticleResult(**r) for r in results],
        latency_ms=round(latency_ms, 2),
    )


# --- Static frontend ---

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="static")

    @app.get("/{full_path:path}", response_model=None)
    async def serve_spa(full_path: str):
        file_path = os.path.join(FRONTEND_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))