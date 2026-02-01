from pydantic_settings import BaseSettings
import os
import logging


class KafkaSettings(BaseSettings):
    bootstrap_servers: str = "localhost:9092"
    orders_topic: str = "orders"
    
    class Config:
        env_prefix = "KAFKA_"


logger = logging.getLogger(__name__)
kafka_settings = KafkaSettings()
logger.debug(
    "KafkaSettings initialized (bootstrap=%s, topic=%s, env=%s)",
    kafka_settings.bootstrap_servers,
    kafka_settings.orders_topic,
    os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
)
