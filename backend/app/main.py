"""FastAPI application factory for the Career Intelligence Platform."""

from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi.errors import RateLimitExceeded

from app.api.rate_limit import limiter
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import set_request_context, start_request_context

logger = logging.getLogger("app.main")

prometheus_instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: initialise infrastructure."""
    logger.info(
        "app_starting",
        extra={"app": settings.app_name, "version": settings.app_version},
    )
    # Warm up the model cache in the background (non-blocking).
    try:
        from app.ml.model_loader import ModelLoader

        ModelLoader.instance().load()
    except Exception as exc:  # pragma: no cover - warm-up is best-effort
        logger.warning("model warm-up failed: %s", exc)
    prometheus_instrumentator.expose(app, endpoint="/metrics")
    yield
    logger.info("app_stopping")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered platform for salary prediction, resume analysis, "
        "skill-gap detection, learning recommendations and job matching.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request correlation + logging middleware
    @app.middleware("http")
    async def request_context_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("x-request-id")
        start_request_context(request_id=request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "http_request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": getattr(locals().get("response", None), "status_code", None),
                    "duration_ms": round(duration_ms, 3),
                    "client": request.client.host if request.client else "",
                },
            )
        set_request_context()  # clear context after each request
        return response

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

    # Exception handlers
    register_exception_handlers(app)

    # Prometheus metrics
    prometheus_instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    # Routers
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", tags=["root"])
    def root() -> dict:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health/ready",
        }

    return app


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "rate_limit_exceeded",
                "message": "Rate limit exceeded, please retry later",
                "path": request.url.path,
            }
        },
    )


app = create_app()
