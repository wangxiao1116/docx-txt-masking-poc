from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings
from app.db.session import Base, engine
from app.models import FileTask, SensitiveEntityRecord
from app.schemas.file_task import ApiResponse


def api_error(code: int, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ApiResponse(code=code, message=message, data=None).model_dump(mode="json"),
    )


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)
    application = FastAPI(title=settings.app_name)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return api_error(exc.status_code, str(exc.detail), exc.status_code)

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return api_error(42200, "request validation failed", 422)

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return api_error(50000, "internal server error", 500)

    application.include_router(router, prefix=settings.api_prefix)
    return application


app = create_app()
