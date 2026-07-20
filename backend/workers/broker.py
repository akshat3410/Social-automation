import dramatiq
from dramatiq.brokers.redis import RedisBroker
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
broker = RedisBroker(url=redis_url)
dramatiq.set_broker(broker)

def get_broker():
    return broker
