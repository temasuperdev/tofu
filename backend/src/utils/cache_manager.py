from flask_caching import Cache
import redis
import os

class CacheManager:
    def __init__(self, app=None):
        self.cache = None
        self.redis_client = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Инициализация кэширования для Flask приложения
        """
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        
        # Инициализируем кэш
        app.config['CACHE_TYPE'] = 'redis'
        app.config['CACHE_REDIS_URL'] = redis_url
        app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 минут по умолчанию
        
        self.cache = Cache(app)
        self.redis_client = redis.from_url(redis_url)

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
        return self.cache.set(key, value, timeout=timeout)

    def get(self, key):
        """
        Получение значения из кэша
        """
        return self.cache.get(key)

    def delete(self, key):
        """
        Удаление ключа из кэша
        """
        return self.cache.delete(key)

    def clear(self):
        """
        Очистка всего кэша
        """
        return self.cache.clear()

# Глобальный экземпляр для использования в приложении
cache_manager = CacheManager()