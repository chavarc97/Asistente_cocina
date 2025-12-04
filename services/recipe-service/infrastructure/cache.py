# ==============================================
# CACHE SERVICE
# Demuestra: Caching Pattern, Performance Optimization
# ==============================================

import redis.asyncio as redis
import json
import logging
from typing import Optional, List, Any
from datetime import timedelta

logger = logging.getLogger(__name__)


class CacheService:
    """
    Servicio de caché usando Redis
    Demuestra: Cache-Aside Pattern
    """
    
    # TTL por defecto para diferentes tipos de datos
    DEFAULT_TTL = timedelta(hours=24)
    RECIPE_TTL = timedelta(days=7)
    SEARCH_TTL = timedelta(hours=24)
    USER_SESSION_TTL = timedelta(hours=24)
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Conectar a Redis"""
        try:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self._client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None
    
    async def disconnect(self):
        """Desconectar de Redis"""
        if self._client:
            await self._client.close()
            logger.info("Disconnected from Redis cache")
    
    @property
    def is_connected(self) -> bool:
        return self._client is not None
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtener valor del caché"""
        if not self._client:
            return None
        
        try:
            value = await self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[timedelta] = None
    ) -> bool:
        """Guardar valor en caché"""
        if not self._client:
            return False
        
        try:
            serialized = json.dumps(value)
            ttl = ttl or self.DEFAULT_TTL
            await self._client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Eliminar valor del caché"""
        if not self._client:
            return False
        
        try:
            await self._client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Verificar si existe una clave"""
        if not self._client:
            return False
        
        try:
            return await self._client.exists(key) > 0
        except Exception as e:
            logger.warning(f"Cache exists error for key {key}: {e}")
            return False
    
    # === Métodos específicos para recetas ===
    
    def _recipe_key(self, recipe_id: str) -> str:
        return f"recipe:{recipe_id}"
    
    def _search_key(self, query: str) -> str:
        return f"search:{query.lower().replace(' ', '_')}"
    
    def _user_session_key(self, user_id: str) -> str:
        return f"session:{user_id}"
    
    async def get_recipe(self, recipe_id: str) -> Optional[dict]:
        """Obtener receta del caché"""
        key = self._recipe_key(recipe_id)
        recipe = await self.get(key)
        
        if recipe:
            # Incrementar contador de accesos
            await self._increment_access_count(key)
        
        return recipe
    
    async def set_recipe(self, recipe_id: str, recipe_data: dict) -> bool:
        """Guardar receta en caché"""
        key = self._recipe_key(recipe_id)
        return await self.set(key, recipe_data, self.RECIPE_TTL)
    
    async def get_search_results(self, query: str) -> Optional[dict]:
        """Obtener resultados de búsqueda del caché"""
        key = self._search_key(query)
        return await self.get(key)
    
    async def set_search_results(self, query: str, results: dict) -> bool:
        """Guardar resultados de búsqueda en caché"""
        key = self._search_key(query)
        return await self.set(key, results, self.SEARCH_TTL)
    
    async def get_user_session(self, user_id: str) -> Optional[dict]:
        """Obtener sesión de usuario"""
        key = self._user_session_key(user_id)
        return await self.get(key)
    
    async def set_user_session(self, user_id: str, session_data: dict) -> bool:
        """Guardar sesión de usuario"""
        key = self._user_session_key(user_id)
        return await self.set(key, session_data, self.USER_SESSION_TTL)
    
    async def _increment_access_count(self, key: str):
        """Incrementar contador de accesos (para estadísticas)"""
        if not self._client:
            return
        
        try:
            count_key = f"{key}:access_count"
            await self._client.incr(count_key)
        except Exception:
            pass  # No es crítico
    
    async def clear_expired(self):
        """
        Limpiar entradas expiradas
        Nota: Redis maneja esto automáticamente con TTL,
        pero este método puede usarse para limpieza manual
        """
        logger.info("Cache cleanup triggered (handled by Redis TTL)")


# Singleton instance
_cache_instance: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Factory function para obtener servicio de caché singleton"""
    global _cache_instance
    if _cache_instance is None:
        import os
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        _cache_instance = CacheService(redis_url)
    return _cache_instance


# ==============================================
# CACHE MANAGER (Alias for CacheService)
# ==============================================

class CacheManager(CacheService):
    """
    Alias para CacheService para mantener compatibilidad
    con la nomenclatura del sistema
    """
    
    async def ping(self) -> bool:
        """Verificar conexión con Redis"""
        if not self._client:
            return False
        try:
            await self._client.ping()
            return True
        except Exception as e:
            logger.error(f"Cache ping failed: {e}")
            return False