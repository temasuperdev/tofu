from flask_caching import Cache
import redis
import os
import logging

class CacheManager:
    def __init__(self, app=None):
        self.cache = None
        self.redis_client = None
        self.logger = logging.getLogger(__name__)
        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Инициализация кэширования для Flask приложения
        """
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        
        try:
            # Инициализируем кэш
            app.config['CACHE_TYPE'] = 'redis'
            app.config['CACHE_REDIS_URL'] = redis_url
            app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 минут по умолчанию
            
            self.cache = Cache(app)
            self.redis_client = redis.from_url(redis_url)
            self.logger.info("Redis cache initialized successfully")
        except Exception as e:
            # Если Redis недоступен, используем простой кэш в памяти
            self.logger.warning(f"Redis not available: {e}. Using simple cache instead.")
            app.config['CACHE_TYPE'] = 'simple'
            self.cache = Cache(app)
            self.redis_client = None

    def get_cache(self):
        """
        Получение экземпляра кэша
        """
        return self.cache

    def get_redis_client(self):
        """
        Получение клиента Redis
        """
        return self.redis_client

    def set(self, key, value, timeout=None):
        """
        Установка значения в кэш
        """
        try:
            return self.cache.set(key, value, timeout=timeout)
        except Exception as e:
            self.logger.warning(f"Cache set error: {e}")
            return None

    def get(self, key):
        """
        Получение значения из кэша
        """
        try:
            return self.cache.get(key)
        except Exception as e:
            self.logger.warning(f"Cache get error: {e}")
            return None

    def delete(self, key):
        """
        Удаление ключа из кэша
        """
        try:
            return self.cache.delete(key)
        except Exception as e:
            self.logger.warning(f"Cache delete error: {e}")
            return None

    def clear(self):
        """
        Очистка всего кэша
        """
        try:
            return self.cache.clear()
        except Exception as e:
            self.logger.warning(f"Cache clear error: {e}")
            return None

# Глобальный экземпляр для использования в приложении
cache_manager = CacheManager()