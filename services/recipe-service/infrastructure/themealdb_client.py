# ==============================================
# THEMEALDB API CLIENT
# Demuestra: External API Integration, Adapter Pattern
# ==============================================

import aiohttp
import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from domain.entities import Recipe, RecipeId, Ingredient

logger = logging.getLogger(__name__)


class TheMealDBClient:
    """
    Cliente para la API de TheMealDB
    Demuestra: Adapter Pattern - adapta API externa a nuestro dominio
    """
    
    BASE_URL = "https://www.themealdb.com/api/json/v1/1"
    
    def __init__(self, timeout: int = 10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtiene o crea sesión HTTP"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session
    
    async def close(self):
        """Cierra la sesión HTTP"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _make_request(self, endpoint: str, params: Dict[str, str] = None) -> Dict[str, Any]: # type: ignore
        """
        Realiza una petición GET a la API
        """
        session = await self._get_session()
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return data
        except aiohttp.ClientError as e:
            logger.error(f"Error calling TheMealDB API: {e}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"Timeout calling TheMealDB API: {url}")
            raise
    
    async def search_by_ingredient(self, ingredient: str) -> List[Recipe]:
        """
        Busca recetas por ingrediente
        Endpoint: filter.php?i={ingredient}
        
        Nota: Este endpoint solo retorna datos básicos,
        necesitamos llamar a lookup para detalles completos
        """
        logger.info(f"Searching recipes with ingredient: {ingredient}")
        
        try:
            data = await self._make_request("filter.php", {"i": ingredient})
            
            if not data.get('meals'):
                logger.info(f"No recipes found for ingredient: {ingredient}")
                return []
            
            # El endpoint filter solo retorna id, name, image
            # Necesitamos obtener detalles completos
            recipes = []
            for meal_preview in data['meals'][:10]:  # Limitar a 10 resultados
                try:
                    full_recipe = await self.get_recipe_by_id(meal_preview['idMeal'])
                    if full_recipe:
                        recipes.append(full_recipe)
                except Exception as e:
                    logger.warning(f"Error getting recipe {meal_preview['idMeal']}: {e}")
            
            logger.info(f"Found {len(recipes)} recipes for ingredient: {ingredient}")
            return recipes
            
        except Exception as e:
            logger.error(f"Error searching by ingredient: {e}")
            return []
    
    async def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """
        Obtiene receta completa por ID
        Endpoint: lookup.php?i={id}
        """
        logger.debug(f"Getting recipe details for ID: {recipe_id}")
        
        try:
            data = await self._make_request("lookup.php", {"i": recipe_id})
            
            if not data.get('meals') or len(data['meals']) == 0:
                return None
            
            # Convertir de formato TheMealDB a nuestro dominio
            return Recipe.from_themealdb(data['meals'][0])
            
        except Exception as e:
            logger.error(f"Error getting recipe by ID {recipe_id}: {e}")
            return None
    
    async def get_random_recipe(self) -> Optional[Recipe]:
        """
        Obtiene una receta aleatoria
        Endpoint: random.php
        """
        logger.info("Getting random recipe")
        
        try:
            data = await self._make_request("random.php")
            
            if not data.get('meals') or len(data['meals']) == 0:
                return None
            
            return Recipe.from_themealdb(data['meals'][0])
            
        except Exception as e:
            logger.error(f"Error getting random recipe: {e}")
            return None
    
    async def search_by_category(self, category: str) -> List[Recipe]:
        """
        Busca recetas por categoría
        Endpoint: filter.php?c={category}
        
        Categorías válidas: Vegetarian, Vegan, Seafood, Dessert, etc.
        """
        logger.info(f"Searching recipes in category: {category}")
        
        try:
            data = await self._make_request("filter.php", {"c": category})
            
            if not data.get('meals'):
                return []
            
            recipes = []
            for meal_preview in data['meals'][:10]:
                try:
                    full_recipe = await self.get_recipe_by_id(meal_preview['idMeal'])
                    if full_recipe:
                        recipes.append(full_recipe)
                except Exception as e:
                    logger.warning(f"Error getting recipe {meal_preview['idMeal']}: {e}")
            
            return recipes
            
        except Exception as e:
            logger.error(f"Error searching by category: {e}")
            return []
    
    async def search_by_name(self, name: str) -> List[Recipe]:
        """
        Busca recetas por nombre
        Endpoint: search.php?s={name}
        """
        logger.info(f"Searching recipes by name: {name}")
        
        try:
            data = await self._make_request("search.php", {"s": name})
            
            if not data.get('meals'):
                return []
            
            recipes = [
                Recipe.from_themealdb(meal) 
                for meal in data['meals']
            ]
            
            return recipes
            
        except Exception as e:
            logger.error(f"Error searching by name: {e}")
            return []
    
    async def get_categories(self) -> List[Dict[str, str]]:
        """
        Obtiene lista de categorías disponibles
        Endpoint: categories.php
        """
        try:
            data = await self._make_request("categories.php")
            
            if not data.get('categories'):
                return []
            
            return [
                {
                    'id': cat['idCategory'],
                    'name': cat['strCategory'],
                    'description': cat.get('strCategoryDescription', ''),
                    'image': cat.get('strCategoryThumb', '')
                }
                for cat in data['categories']
            ]
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    async def search_by_multiple_ingredients(
        self, 
        ingredients: List[str]
    ) -> List[Recipe]:
        """
        Busca recetas que contengan múltiples ingredientes
        
        Nota: TheMealDB no soporta búsqueda por múltiples ingredientes,
        así que buscamos por el primer ingrediente y filtramos resultados
        """
        if not ingredients:
            return []
        
        logger.info(f"Searching recipes with ingredients: {ingredients}")
        
        # Buscar por el primer ingrediente
        primary_results = await self.search_by_ingredient(ingredients[0])
        
        if len(ingredients) == 1:
            return primary_results
        
        # Filtrar resultados que contengan los otros ingredientes
        other_ingredients = [ing.lower() for ing in ingredients[1:]]
        
        filtered_recipes = []
        for recipe in primary_results:
            recipe_ingredients = [
                ing.name.lower() for ing in recipe.ingredients
            ]
            
            # Verificar si contiene al menos uno de los otros ingredientes
            if any(
                any(other in rec_ing for rec_ing in recipe_ingredients)
                for other in other_ingredients
            ):
                filtered_recipes.append(recipe)
        
        logger.info(
            f"Filtered to {len(filtered_recipes)} recipes matching multiple ingredients"
        )
        
        return filtered_recipes


# Singleton instance
_client_instance: Optional[TheMealDBClient] = None


def get_themealdb_client() -> TheMealDBClient:
    """Factory function para obtener cliente singleton"""
    global _client_instance
    if _client_instance is None:
        _client_instance = TheMealDBClient()
    return _client_instance