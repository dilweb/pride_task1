from contextlib import asynccontextmanager
import logging
import time
from fastapi import FastAPI, Request
import uvicorn

from orderservice.api.routers import router
from orderservice.kafka.producer import get_producer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    - Код до yield: выполняется при старте
    - Код после yield: выполняется при остановке
    """
    logger.info("Order Service запускается...")
    producer = get_producer()
    logger.info("Order Service готов к работе")
    
    yield
    
    logger.info("Order Service останавливается...")
    from orderservice.kafka.producer import _order_producer
    if _order_producer:
        _order_producer.close()
    logger.info("Order Service остановлен")


app = FastAPI(
    title="Order Service",
    version="1.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "HTTP %s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(router, prefix="/api", tags=["orders"])


def start_app():
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start_app()
