import redis

pool = redis.ConnectionPool(
    host="localhost",
    port=6379,
    max_connections=50,
    decode_responses=True
)

redis_client = redis.Redis(connection_pool=pool)