import logging

import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.errors import AppError
from src.schemas import ErrorResponse


logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def error_response(
    request: Request,
    status_code: int,
    message: str,
) -> JSONResponse:
    request_id = get_request_id(request)
    body = ErrorResponse(
        code=status_code,
        message=message,
        request_id=request_id,
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(),
        headers={"X-Request-ID": request_id},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(
        request: Request,
        exc: AppError,
    ) -> JSONResponse:
        request_id = get_request_id(request)
        logger.warning(
            "application_error request_id=%s status=400",
            request_id,
        )
        return error_response(request, 400, str(exc))

    @app.exception_handler(requests.Timeout)
    async def handle_timeout(
        request: Request,
        _exc: requests.Timeout,
    ) -> JSONResponse:
        request_id = get_request_id(request)
        logger.error(
            "upstream_timeout request_id=%s status=504",
            request_id,
        )
        return error_response(request, 504, "模型服务响应超时")

    @app.exception_handler(Exception)
    async def handle_unknown_error(
        request: Request,
        _exc: Exception,
    ) -> JSONResponse:
        return error_response(request, 500, "服务器内部错误")
