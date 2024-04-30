import structlog
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from src.app.core.config import settings
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.stdlib.get_logger(settings.LOG_NAME)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as http_exception:
            return JSONResponse(
                status_code=http_exception.status_code,
                content={"error": "Client Error", "message": str(http_exception.detail)},
            )
        except Exception as e:
            logger.exception(
                "An unhandled exception was caught by last resort middleware",
                exception_class=e.__class__.__name__,
                exc_info=e,
            )
            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error", "message": "An unexpected error occurred."},
            )
