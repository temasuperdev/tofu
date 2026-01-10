from flask_caching import Cache
import redis
import os
import logging
from typing import Optional

class CacheManager:
    def __init__(self, app=None):
        self.cache = None
        self.redis_client = None
        self.logger = logging.getLogger(__name__)
        self.redis_available = False
        self.redis_error_logged = False  # Флаг для однократного логирования ошибки
        self.redis_url: Optional[str] = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Инициализация кэширования для Flask приложения
        """
        self.redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        
        try:
            # Инициализируем кэш
            app.config['CACHE_TYPE'] = 'redis'
            app.config['CACHE_REDIS_URL'] = self.redis_url
            app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 минут по умолчанию
            
            self.cache = Cache(app)
            self.redis_client = redis.from_url(self.redis_url, socket_connect_timeout=5, socket_timeout=5)
            # Проверяем подключение
            self.redis_client.ping()
            self.redis_available = True
            self.logger.info(f"Redis cache initialized successfully (redis_url={self.redis_url})")
        except Exception as e:
            # Если Redis недоступен, используем простой кэш в памяти
            self.redis_available = False
            error_type = type(e).__name__
            self.logger.warning(
                f"Redis not available, using simple cache instead (redis_url={self.redis_url}, "
                f"error={str(e)}, error_type={error_type})"
            )
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

    def set(self, key: str, value, timeout: Optional[int] = None) -> Optional[bool]:
        """
        Установка значения в кэш
        """
        if not self.redis_available and not self.redis_error_logged:
            # Логируем только один раз, если Redis недоступен
            self.logger.debug(f"Using simple cache (Redis unavailable, redis_url={self.redis_url})")
            self.redis_error_logged = True
        
        try:
            return self.cache.set(key, value, timeout=timeout)
        except Exception as e:
            # Логируем ошибки только при работе с Redis (не для simple cache)
            if self.redis_available and not self.redis_error_logged:
                error_type = type(e).__name__
                self.logger.warning(
                    f"Cache operation failed, falling back to no-cache mode "
                    f"(operation=set, key={key}, error={str(e)}, error_type={error_type})"
                )
                self.redis_error_logged = True
                # Переключаемся на simple cache при ошибке
                self.redis_available = False
            return None

    def get(self, key: str):
        """
        Получение значения из кэша
        """
        if not self.redis_available and not self.redis_error_logged:
            # Логируем только один раз, если Redis недоступен
            self.logger.debug(f"Using simple cache (Redis unavailable, redis_url={self.redis_url})")
            self.redis_error_logged = True
        
        try:
            return self.cache.get(key)
        except Exception as e:
            # Логируем ошибки только при работе с Redis (не для simple cache)
            if self.redis_available and not self.redis_error_logged:
                error_type = type(e).__name__
                self.logger.warning(
                    f"Cache operation failed, falling back to no-cache mode "
                    f"(operation=get, key={key}, error={str(e)}, error_type={error_type})"
                )
                self.redis_error_logged = True
                # Переключаемся на simple cache при ошибке
                self.redis_available = False
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

    def has(self, key: str) -> bool:
        """
        Проверка наличия ключа в кэше
        """
        try:
            return self.cache.has(key)
        except Exception as e:
            self.logger.warning(f"Cache has error: {e}")
            return False

# Глобальный экземпляр для использования в приложении
cache_manager = CacheManager()