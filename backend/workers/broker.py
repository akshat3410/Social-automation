import dramatiq
from dramatiq.brokers.redis import RedisBroker

from config.settings import get_settings

broker = RedisBroker(url=get_settings().REDIS_URL)
dramatiq.set_broker(broker)


def get_broker() -> RedisBroker:
    return broker
