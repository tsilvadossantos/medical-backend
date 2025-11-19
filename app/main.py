"""
Main application module.

Entry point for the FastAPI application. Configures routes,
middleware, and startup/shutdown events.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging_config import setup_logging
from app.core.settings import settings
from app.core.metrics import init_app_info, HEALTH_CHECK_STATUS
from app.db.init_db import init_db, seed_sample_data
from app.db.session import SessionLocal
from app.api.v1 import health, patients, notes, summary, metrics
from app.middleware.metrics_middleware import MetricsMiddleware

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="API for managing patient records and generating summaries",
    version=settings.APP_VERSION,
    docs_url="/docs" if getattr(settings, 'DEBUG', True) else None,
    redoc_url="/redoc" if getattr(settings, 'DEBUG', True) else None,
)

# Configure CORS based on environment
cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else []
if settings.CORS_ORIGINS == "*":
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware
if settings.METRICS_ENABLED:
    app.add_middleware(MetricsMiddleware)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all incoming requests.

    Logs request method, URL, and response status code.
    """
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Logs the error and returns a generic 500 response.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.

    Initializes database, seeds sample data, and sets up metrics.
    """
    logger.info(f"Starting application in {settings.APP_ENV} mode...")

    # Initialize metrics
    if settings.METRICS_ENABLED:
        init_app_info(settings.APP_VERSION, settings.APP_ENV)
        HEALTH_CHECK_STATUS.labels(component='app').set(1)

    init_db()

    db = SessionLocal()
    try:
        seed_sample_data(db)
    finally:
        db.close()

    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    """
    logger.info("Shutting down application...")
    if settings.METRICS_ENABLED:
        HEALTH_CHECK_STATUS.labels(component='app').set(0)


# Include routers
app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(patients.router)
app.include_router(notes.router)
app.include_router(summary.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
