import redis
from redis import ConnectionError

def redis_connection():
    try:
        cache = redis.Redis(host="localhost", db=1)
        return cache
    except redis.exceptions.ConnectionError as ce:
        raise f"connection error {ce}"