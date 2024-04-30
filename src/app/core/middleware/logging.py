import time
from typing import TypedDict

import structlog
from asgi_correlation_id import correlation_id
from asgiref.typing import (
    ASGI3Application,
    ASGIReceiveCallable,
    ASGISendCallable,
    ASGISendEvent,
    HTTPScope,
)
from src.app.core.config import settings
from uvicorn.protocols.utils import get_path_with_query_string

access_logger = structlog.stdlib.get_logger(settings.LOG_ACCESS_NAME)


class AccessInfo(TypedDict, total=False):
    response: ASGISendEvent
    start_time: float
    end_time: float


class StructLogMiddleware:
    def __init__(self, app: ASGI3Application):
        self.app = app
        pass

    async def __call__(self, scope: HTTPScope, receive: ASGIReceiveCallable, send: ASGISendCallable):
        # If the request is not an HTTP request, we don't need to do anything special
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        structlog.contextvars.clear_contextvars()
        # These context vars will be added to all log entries emitted during the request
        request_id = correlation_id.get()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        info = AccessInfo()

        # Inner send function
        async def inner_send(message):
            if message["type"] == "http.response.start":
                info["response"] = message
            await send(message)

        try:
            info["start_time"] = time.perf_counter_ns()
            await self.app(scope, receive, inner_send)
        except Exception:
            raise
        finally:
            info["end_time"] = time.perf_counter_ns()
            process_time = info["end_time"] - info["start_time"]
            try:
                status_code = info["response"]["status"]
            except KeyError:
                status_code = 500
            client_host, client_port = scope["client"]
            http_method = scope["method"]
            http_version = scope["http_version"]
            url = get_path_with_query_string(scope)

            # Recreate the Uvicorn access log format, but add all parameters as structured information
            access_logger.info(
                f"""{client_host}:{client_port} - "{http_method} {scope["path"]} HTTP/{http_version}" {status_code}""",
                http={
                    "url": str(url),
                    "status_code": status_code,
                    "method": http_method,
                    "request_id": request_id,
                    "version": http_version,
                },
                network={"client": {"ip": client_host, "port": client_port}},
                duration=process_time,
            )
