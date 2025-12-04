# ==============================================
# DATABASE CONNECTION
# Demuestra: Connection Pooling, Resource Management
# ==============================================

import asyncpg
import os
import json
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class Database:
    """
    Gestor de conexiones a PostgreSQL
    Demuestra: Single Responsibility (solo maneja conexiones)
    """
    
    def __init__(self, connection_url: str = None):
        self.connection_url = connection_url or os.getenv("DATABASE_URL")
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Crear pool de conexiones"""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    
    async def disconnect(self):
        """Cerrar pool de conexiones"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    def acquire(self):
        """Adquirir conexión del pool"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        return self.pool.acquire()
    
    async def execute(self, query: str, *args):
        """Ejecutar query"""
        async with self.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Fetch múltiples filas"""
        async with self.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Fetch una fila"""
        async with self.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Fetch un valor"""
        async with self.acquire() as connection:
            return await connection.fetchval(query, *args)


# Singleton instance
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """Factory function para obtener database singleton"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


# ==============================================
# DATABASE MANAGER (Extends Database with business logic)
# ==============================================

class DatabaseManager(Database):
    """
    Gestor de base de datos con métodos de negocio
    Extiende Database con operaciones específicas del dominio
    """
    
    async def check_connection(self) -> bool:
        """Verificar conexión a base de datos"""
        try:
            await self.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    async def save_search_history(self, user_id: str, ingredients: List[str], results_count: int):
        """Guardar historial de búsqueda"""
        query = """
            INSERT INTO search_history (user_id, search_query, ingredients, results_count)
            VALUES (
                (SELECT id FROM users WHERE telegram_id = $1),
                $2,
                $3::jsonb,
                $4
            )
        """
        try:
            await self.execute(
                query,
                user_id,
                " ".join(ingredients),
                json.dumps(ingredients),
                results_count
            )
            logger.debug(f"Saved search history for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save search history: {e}")
            raise
    
    async def get_user_favorites(self, user_id: str) -> List[dict]:
        """Obtener favoritos de usuario"""
        query = """
            SELECT recipe_id, recipe_name, recipe_image, added_at
            FROM favorites
            WHERE user_id = (SELECT id FROM users WHERE telegram_id = $1)
            AND status = 'active'
            ORDER BY added_at DESC
            LIMIT 10
        """
        try:
            rows = await self.fetch(query, user_id)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get favorites: {e}")
            return []
    
    async def add_favorite(self, user_id: str, recipe_id: str, recipe_name: str, recipe_image: str = None) -> bool:
        """Agregar receta a favoritos"""
        # Primero verificar que no exceda el límite de 10
        count_query = """
            SELECT COUNT(*) FROM favorites
            WHERE user_id = (SELECT id FROM users WHERE telegram_id = $1)
            AND status = 'active'
        """
        
        try:
            count = await self.fetchval(count_query, user_id)
            if count >= 10:
                logger.warning(f"User {user_id} has reached favorites limit")
                return False
            
            insert_query = """
                INSERT INTO favorites (user_id, recipe_id, recipe_name, recipe_image)
                VALUES (
                    (SELECT id FROM users WHERE telegram_id = $1),
                    $2, $3, $4
                )
                ON CONFLICT (user_id, recipe_id) DO UPDATE
                SET status = 'active', added_at = CURRENT_TIMESTAMP
            """
            await self.execute(insert_query, user_id, recipe_id, recipe_name, recipe_image)
            logger.info(f"Added recipe {recipe_id} to favorites for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add favorite: {e}")
            return False
    
    async def remove_favorite(self, user_id: str, recipe_id: str) -> bool:
        """Eliminar receta de favoritos"""
        query = """
            UPDATE favorites
            SET status = 'removed'
            WHERE user_id = (SELECT id FROM users WHERE telegram_id = $1)
            AND recipe_id = $2
        """
        try:
            await self.execute(query, user_id, recipe_id)
            logger.info(f"Removed recipe {recipe_id} from favorites for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove favorite: {e}")
            return False
    
    async def get_user_search_history(self, user_id: str, limit: int = 5) -> List[dict]:
        """Obtener historial de búsquedas recientes"""
        query = """
            SELECT search_query, ingredients, searched_at
            FROM search_history
            WHERE user_id = (SELECT id FROM users WHERE telegram_id = $1)
            ORDER BY searched_at DESC
            LIMIT $2
        """
        try:
            rows = await self.fetch(query, user_id, limit)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get search history: {e}")
            return []
    
    async def create_or_update_user(self, telegram_id: int, username: str = None, 
                                   first_name: str = None, last_name: str = None) -> str:
        """Crear o actualizar usuario"""
        query = """
            INSERT INTO users (telegram_id, username, first_name, last_name)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (telegram_id) DO UPDATE
            SET username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                last_active = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """
        try:
            user_id = await self.fetchval(query, telegram_id, username, first_name, last_name)
            return str(user_id)
        except Exception as e:
            logger.error(f"Failed to create/update user: {e}")
            raise
    
    async def get_user_filter(self, user_id: str) -> str:
        """Obtener filtro dietético del usuario"""
        query = """
            SELECT dietary_filter FROM users
            WHERE telegram_id = $1
        """
        try:
            filter_value = await self.fetchval(query, user_id)
            return filter_value or "none"
        except Exception as e:
            logger.error(f"Failed to get user filter: {e}")
            return "none"
    
    async def update_user_filter(self, user_id: str, dietary_filter: str) -> bool:
        """Actualizar filtro dietético del usuario"""
        query = """
            UPDATE users
            SET dietary_filter = $2::dietary_filter,
                updated_at = CURRENT_TIMESTAMP
            WHERE telegram_id = $1
        """
        try:
            await self.execute(query, user_id, dietary_filter)
            logger.info(f"Updated dietary filter to {dietary_filter} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update user filter: {e}")
            return False