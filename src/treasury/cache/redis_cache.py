\
\
\
\

import redis
import pickle
import json
import hashlib
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import pandas as pd

from ..logging_config import logger


class RedisCache:
\
\
\
\

    def __init__(self,
                 host: str = 'localhost',
                 port: int = 6379,
                 db: int = 0,
                 password: Optional[str] = None,
                 prefix: str = 'scalar:'):

        self.prefix = prefix
        self.default_ttl = 3600

        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5
            )


            self.redis_client.ping()
            self.is_connected = True
            logger.info(f"SUCCESS Redis connecté: {host}:{port}")

        except (redis.RedisError, ConnectionError) as e:
            logger.warning(f"WARNING Redis non disponible: {e}")
            self.redis_client = None
            self.is_connected = False

    def _make_key(self, key: str) -> str:
        \
        return f"{self.prefix}{key}"

    def _serialize_data(self, data: Any) -> bytes:
        \
        if isinstance(data, pd.DataFrame):

            return pickle.dumps({
                'type': 'dataframe',
                'data': data.to_dict('records'),
                'columns': list(data.columns),
                'index': list(data.index)
            })
        elif isinstance(data, (dict, list)):

            return json.dumps({
                'type': 'json',
                'data': data
            }).encode('utf-8')
        else:

            return pickle.dumps({
                'type': 'pickle',
                'data': data
            })

    def _deserialize_data(self, serialized: bytes) -> Any:
        \
        try:

            try:
                json_data = json.loads(serialized.decode('utf-8'))
                if json_data.get('type') == 'json':
                    return json_data['data']
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass


            pickled_data = pickle.loads(serialized)

            if pickled_data.get('type') == 'dataframe':

                return pd.DataFrame(
                    pickled_data['data'],
                    columns=pickled_data['columns'],
                    index=pickled_data['index']
                )
            elif pickled_data.get('type') == 'json':
                return pickled_data['data']
            else:
                return pickled_data.get('data')

        except Exception as e:
            logger.error(f"Erreur désérialisation Redis: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        \
        if not self.is_connected:
            return False

        try:
            redis_key = self._make_key(key)
            serialized = self._serialize_data(value)
            ttl = ttl or self.default_ttl

            result = self.redis_client.setex(redis_key, ttl, serialized)

            if result:
                logger.debug(f"SUCCESS Redis SET: {key} (TTL: {ttl}s)")

            return result

        except Exception as e:
            logger.error(f"ERROR Redis SET error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        \
        if not self.is_connected:
            return None

        try:
            redis_key = self._make_key(key)
            serialized = self.redis_client.get(redis_key)

            if serialized is None:
                logger.debug(f"ERROR Redis MISS: {key}")
                return None

            data = self._deserialize_data(serialized)
            logger.debug(f"SUCCESS Redis HIT: {key}")
            return data

        except Exception as e:
            logger.error(f"ERROR Redis GET error: {e}")
            return None

    def delete(self, key: str) -> bool:
        \
        if not self.is_connected:
            return False

        try:
            redis_key = self._make_key(key)
            result = self.redis_client.delete(redis_key)
            logger.debug(f"Redis DELETE: {key}")
            return result > 0

        except Exception as e:
            logger.error(f"ERROR Redis DELETE error: {e}")
            return False

    def exists(self, key: str) -> bool:
        \
        if not self.is_connected:
            return False

        try:
            redis_key = self._make_key(key)
            return self.redis_client.exists(redis_key) > 0
        except:
            return False

    def get_ttl(self, key: str) -> int:
        \
        if not self.is_connected:
            return -2

        try:
            redis_key = self._make_key(key)
            return self.redis_client.ttl(redis_key)
        except:
            return -2

    def clear_pattern(self, pattern: str) -> int:
        \
        if not self.is_connected:
            return 0

        try:
            redis_pattern = self._make_key(pattern)
            keys = self.redis_client.keys(redis_pattern)

            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Redis cleared {deleted} keys matching: {pattern}")
                return deleted

            return 0

        except Exception as e:
            logger.error(f"ERROR Redis clear pattern error: {e}")
            return 0

    def get_cache_stats(self) -> Dict[str, Any]:
        \
        if not self.is_connected:
            return {'status': 'disconnected'}

        try:
            info = self.redis_client.info()
            scalar_keys = self.redis_client.keys(f"{self.prefix}*")

            return {
                'status': 'connected',
                'redis_version': info.get('redis_version'),
                'used_memory_human': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_keys': info.get('db0', {}).get('keys', 0),
                'scalar_keys': len(scalar_keys),
                'hit_rate': self._calculate_hit_rate(info)
            }

        except Exception as e:
            logger.error(f"ERROR Redis stats error: {e}")
            return {'status': 'error', 'error': str(e)}

    def _calculate_hit_rate(self, info: dict) -> Optional[float]:
        \
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)

        if hits + misses > 0:
            return hits / (hits + misses)
        return None

    def flush_all(self) -> bool:
        \
        if not self.is_connected:
            return False

        try:
            self.redis_client.flushdb()
            logger.warning("CRITICAL Redis DB flushed completely!")
            return True
        except Exception as e:
            logger.error(f"ERROR Redis flush error: {e}")
            return False


class HybridCache:
\
\
\
\

    def __init__(self, redis_config: Optional[Dict] = None):

        self.memory_cache = {}
        self.memory_ttl = {}


        if redis_config:
            self.redis_cache = RedisCache(**redis_config)
        else:
            self.redis_cache = RedisCache()

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
\

        self.memory_cache[key] = value
        if ttl:
            self.memory_ttl[key] = datetime.now() + timedelta(seconds=ttl)


        if self.redis_cache.is_connected:
            return self.redis_cache.set(key, value, ttl)

        return True

    def get(self, key: str) -> Optional[Any]:
\


        if self.redis_cache.is_connected:
            redis_value = self.redis_cache.get(key)
            if redis_value is not None:

                self.memory_cache[key] = redis_value
                return redis_value


        if key in self.memory_cache:

            if key in self.memory_ttl:
                if datetime.now() > self.memory_ttl[key]:

                    del self.memory_cache[key]
                    del self.memory_ttl[key]
                    return None

            return self.memory_cache[key]

        return None

    def delete(self, key: str) -> bool:
        \
        memory_deleted = key in self.memory_cache

        if memory_deleted:
            del self.memory_cache[key]
            if key in self.memory_ttl:
                del self.memory_ttl[key]

        redis_deleted = self.redis_cache.delete(key)

        return memory_deleted or redis_deleted

    def clear_all(self) -> bool:
        \
        self.memory_cache.clear()
        self.memory_ttl.clear()

        if self.redis_cache.is_connected:
            return self.redis_cache.clear_pattern("*")

        return True

    def get_status(self) -> Dict[str, Any]:
        \
        redis_stats = self.redis_cache.get_cache_stats()

        return {
            'memory_cache': {
                'keys_count': len(self.memory_cache),
                'with_ttl': len(self.memory_ttl)
            },
            'redis_cache': redis_stats,
            'fallback_mode': not self.redis_cache.is_connected
        }



def create_production_cache() -> HybridCache:
    \
    import os

    redis_config = None


    if os.getenv('REDIS_HOST'):
        redis_config = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', '6379')),
            'password': os.getenv('REDIS_PASSWORD'),
            'db': int(os.getenv('REDIS_DB', '0'))
        }

    return HybridCache(redis_config)



production_cache = create_production_cache()
