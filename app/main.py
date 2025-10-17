"""Main FastAPI application"""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import select
import logging

from app.config import settings
from app.database import engine, Base, AsyncSessionLocal
from app.logging_config import logger
from app.models import User, UserRole, Device  # Import Device model for SQLAlchemy
from app.auth import get_password_hash
from app.routers import auth, devices, commands, compliance
from app.schemas import HealthResponse
from app import __version__


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up Network API Gateway")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create default admin user if not exists
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.username == settings.default_admin_username)
        )
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            logger.info("Creating default admin user")
            admin_user = User(
                username=settings.default_admin_username,
                email=settings.default_admin_email,
                hashed_password=get_password_hash(settings.default_admin_password),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin_user)
            await db.commit()
            logger.info(f"Default admin user created: {settings.default_admin_username}")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Network API Gateway")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A lightweight, extensible middleware tool that bridges traditional CLI-only network devices with modern REST API management",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request ID middleware
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to each request"""
    import uuid

    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id

    return response


# Include routers
app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(commands.router)
app.include_router(compliance.router)


# Health check endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": __version__,
        "database": "connected",
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check endpoint
    """
    try:
        # Check database connectivity
        async with AsyncSessionLocal() as db:
            await db.execute(select(1))

        return {"status": "ready", "timestamp": datetime.utcnow(), "checks": {"database": "ok"}}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not ready",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            },
        )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Network API Gateway",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.exception(f"Unhandled exception: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
