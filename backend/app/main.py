"""
FastAPI Application Entry Point - Legal Intel Dashboard
"""
# Standard library imports
import time
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

try:
    # Third-party imports
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

# Local application imports
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging_config import RequestLogger, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting up Legal Intel Dashboard API...")

    yield

    # Shutdown
    logger.info("Shutting down Legal Intel Dashboard API...")


# Initialize Sentry for error tracking (if available and configured)
if SENTRY_AVAILABLE and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,  # 10% of transactions
        environment=settings.SENTRY_ENVIRONMENT,
    )

# Create FastAPI application
app = FastAPI(
    title="Legal Intel Dashboard API",
    version=settings.VERSION,
    description="Production-grade API for Legal Intelligence Dashboard with document processing, metadata extraction, and natural language querying",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests with timing"""
    start_time = time.time()

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log request
        await RequestLogger.log_request(request, response, process_time)

        # Add timing header
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))

        return response
    except Exception as e:
        logger.error(
            "Request failed",
            extra={"method": request.method, "path": request.url.path, "error": str(e)},
        )
        raise


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Legal Intel Dashboard API",
        "version": settings.VERSION,
        "status": "running",
        "docs": f"{settings.API_V1_STR}/docs",
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy"}
