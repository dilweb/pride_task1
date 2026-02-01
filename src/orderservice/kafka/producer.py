import json
import threading
import queue
import logging
from confluent_kafka import Producer

from orderservice.kafka.config import kafka_settings

logger = logging.getLogger(__name__)


class AsyncOrderProducer:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.topic = topic
        self.producer = Producer({
            "bootstrap.servers": bootstrap_servers,
            "client.id": "order-service-producer",
            "acks": "all",
            "retries": 3,
            "retry.backoff.ms": 100,
        })
        self._q: queue.Queue[dict] = queue.Queue(maxsize=10000)
        self._stop = threading.Event()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def _delivery_callback(self, err, msg):
        if err:
            logger.error("Kafka delivery failed: %s", err)
        else:
            logger.info("Kafka delivery ok: %s/%s", msg.topic(), msg.offset())

    def _run(self):
        while not self._stop.is_set():
            try:
                order = self._q.get(timeout=0.1)
            except queue.Empty:
                # обслуживаем callbacks, даже если нет новых сообщений
                self.producer.poll(0)
                continue

            try:
                self.producer.produce(
                    topic=self.topic,
                    key=order["order_id"].encode("utf-8"),
                    value=json.dumps(order, ensure_ascii=False).encode("utf-8"),
                    callback=self._delivery_callback,
                )
            except Exception:
                logger.exception("produce() failed")
            finally:
                # важно вызывать poll() чтобы callbacks отрабатывали
                self.producer.poll(0)
                self._q.task_done()

    def publish_async(self, order: dict) -> bool:
        try:
            self._q.put_nowait(order)
            return True
        except queue.Full:
            logger.warning("producer queue full, dropping")
            return False

    def close(self):
        self._stop.set()
        self._worker.join(timeout=2)
        # дожидаемся доставки при остановке
        self.producer.flush(timeout=5)


_order_producer: AsyncOrderProducer | None = None


def get_producer() -> AsyncOrderProducer:
    global _order_producer
    if _order_producer is None:
        _order_producer = AsyncOrderProducer(
            bootstrap_servers=kafka_settings.bootstrap_servers,
            topic=kafka_settings.orders_topic,
        )
    return _order_producer
