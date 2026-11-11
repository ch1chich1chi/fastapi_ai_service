import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from fastapi import Request

from src.exception_handlers import register_exception_handlers
from src.logging_config import configure_logging
from src.routers.chat import router as chat_router
from src.routers.conversations import router as conversations_router

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(chat_router)
app.include_router(conversations_router)
register_exception_handlers(app)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    request.state.request_id = request_id
    start_time = perf_counter()

    logger.info(
        "request_started request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (perf_counter() - start_time) * 1000
        logger.exception(
            "request_failed request_id=%s method=%s path=%s "
            "status=500 elapsed_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            elapsed_ms,
        )
        raise

    elapsed_ms = (perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_finished request_id=%s method=%s path=%s "
        "status=%s elapsed_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
