from typing import Any, Optional
import pickle
import redis

DEFAULT_REDIS_CACHE_EXPIRY = 3600


def set_data_in_redis(key: str, data) -> bool:
    """
    Sets data in Redis cache.
    """
    redis_conn = redis.StrictRedis("redis")
    p_mydict = pickle.dumps(data)
    redis_conn.set(key, p_mydict, ex=DEFAULT_REDIS_CACHE_EXPIRY)
    return True


def get_data_from_redis(key: str) -> Optional[Any]:
    """
    Get data from Redis cache for the key provided.
    """
    redis_conn = redis.StrictRedis("redis")
    read_dict = redis_conn.get(key)
    return pickle.loads(read_dict) if read_dict else None


def delete_data_from_redis(key: str) -> bool:
    """
    Delete specified key from Redis cache.
    """
    redis_conn = redis.StrictRedis("redis")
    redis_conn.delete(key)
    return True
