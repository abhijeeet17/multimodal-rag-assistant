from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.routes import health, documents, chat, feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    settings.create_directories()
    init_db()
    yield
    # Shutdown actions


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Multimodal Document Intelligence and Retrieval-Augmented Generation (RAG) System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api/v1 prefix
app.include_router(health.router, prefix=settings.API_V1_PREFIX, tags=["Health"])
app.include_router(documents.router, prefix=f"{settings.API_V1_PREFIX}/documents", tags=["Documents"])
app.include_router(chat.router, prefix=settings.API_V1_PREFIX, tags=["Chat & RAG"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_PREFIX}/feedback", tags=["Feedback"])


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }
