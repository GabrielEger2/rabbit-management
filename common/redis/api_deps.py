import orjson
from typing import Callable, Any
from .config import redis_client


async def cache_with_expiry(key: str, data_fetcher: Callable[[], Any], ttl: int = 300):
    cached_data = await redis_client.get(key)
    if cached_data:
        return orjson.loads(cached_data)

    data = await data_fetcher()

    await redis_client.set(key, orjson.dumps(data), ex=ttl)
    return data


async def cache_with_sliding_expiry(
    key: str, data_fetcher: Callable[[], Any], ttl: int = 300
):
    cached_data = await redis_client.get(key)
    if cached_data:
        await redis_client.expire(key, ttl)
        return orjson.loads(cached_data)

    data = await data_fetcher()

    await redis_client.set(key, orjson.dumps(data), ex=ttl)
    return data


async def cache_with_access_limit(
    key: str, data_fetcher: Callable[[], Any], max_accesses: int = 10
):
    cached_data = await redis_client.get(key)
    access_count_key = f"{key}:access_count"

    if cached_data:
        access_count = await redis_client.incr(access_count_key)

        if access_count >= max_accesses:
            await redis_client.delete(key)
            await redis_client.delete(access_count_key)
            return await cache_with_access_limit(key, data_fetcher, max_accesses)

        return orjson.loads(cached_data)

    data = await data_fetcher()

    await redis_client.set(key, orjson.dumps(data))
    await redis_client.set(access_count_key, 0)
    return data


async def invalidate_cache(key: str):
    await redis_client.delete(key)


async def invalidate_pattern_cache(pattern: str = "*"):
    print(pattern)
    keys = await redis_client.keys(pattern)
    print(keys)
    if keys:
        await redis_client.delete(*keys)
