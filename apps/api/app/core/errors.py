from typing import Any
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: Any = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", code: str = "not_found"):
        super().__init__(code=code, message=message, status_code=404)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required", code: str = "unauthorized"):
        super().__init__(code=code, message=message, status_code=401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden", code: str = "forbidden"):
        super().__init__(code=code, message=message, status_code=403)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", code: str = "conflict"):
        super().__init__(code=code, message=message, status_code=409)


class QuotaExceededError(AppError):
    def __init__(self, message: str = "Quota exceeded", code: str = "quota_exceeded"):
        super().__init__(code=code, message=message, status_code=429)


def error_body(code: str, message: str, request_id: str, details: Any = None) -> dict[str, Any]:
    body: dict[str, Any] = {"error": {"code": code, "message": message, "request_id": request_id}}
    if details is not None:
        body["error"]["details"] = details
    return body


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.code, exc.message, request_id, exc.details),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    return JSONResponse(
        status_code=500,
        content=error_body("internal_error", "An unexpected error occurred", request_id),
    )
