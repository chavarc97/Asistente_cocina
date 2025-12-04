# ==============================================
# RECIPE SERVICE - MAIN APPLICATION
# FastAPI Application for Recipe Management
# Demuestra: Clean Architecture, Dependency Injection
# ==============================================

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

from domain.entities import Recipe, DietaryFilter
from infrastructure.themealdb_client import TheMealDBClient
from infrastructure.database import DatabaseManager
from infrastructure.cache import CacheManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==============================================
# PYDANTIC MODELS (DTOs)
# ==============================================

class RecipeSearchRequest(BaseModel):
    """Request model for recipe search"""
    ingredients: List[str] = Field(..., min_length=1, max_length=3, description="List of 1-3 ingredients")
    dietary_filter: Optional[str] = Field(None, description="Dietary filter: vegetarian, vegan, gluten_free")
    user_id: Optional[str] = Field(None, description="User ID for search history")


class RecipeResponse(BaseModel):
    """Response model for recipe"""
    id: str
    name: str
    category: str
    area: str
    instructions: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    ingredients: List[dict]
    tags: List[str]
    
    class Config:
        from_attributes = True


class RecipeListResponse(BaseModel):
    """Response model for recipe list"""
    recipes: List[RecipeResponse]
    count: int
    

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    service: str
    database: str
    cache: str
    external_api: str


# ==============================================
# DEPENDENCY INJECTION
# ==============================================

class ServiceContainer:
    """Container for service dependencies"""
    
    def __init__(self):
        self.themealdb_client: Optional[TheMealDBClient] = None
        self.db_manager: Optional[DatabaseManager] = None
        self.cache_manager: Optional[CacheManager] = None
    
    async def initialize(self):
        """Initialize all services"""
        logger.info("Initializing services...")
        
        # Initialize TheMealDB client
        self.themealdb_client = TheMealDBClient()
        
        # Initialize Database
        db_url = os.getenv("DATABASE_URL", "postgresql://chef_user:ChefSecure123!@localhost:5432/chef_db")
        self.db_manager = DatabaseManager(db_url)
        await self.db_manager.connect()
        
        # Initialize Cache
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.cache_manager = CacheManager(redis_url)
        await self.cache_manager.connect()
        
        logger.info("Services initialized successfully")
    
    async def shutdown(self):
        """Cleanup all services"""
        logger.info("Shutting down services...")
        
        if self.themealdb_client:
            await self.themealdb_client.close()
        
        if self.db_manager:
            await self.db_manager.disconnect()
        
        if self.cache_manager:
            await self.cache_manager.disconnect()
        
        logger.info("Services shut down successfully")


# Global service container
services = ServiceContainer()


def get_themealdb_client() -> TheMealDBClient:
    """Dependency to get TheMealDB client"""
    if not services.themealdb_client:
        raise HTTPException(status_code=503, detail="TheMealDB client not initialized")
    return services.themealdb_client


def get_db_manager() -> DatabaseManager:
    """Dependency to get database manager"""
    if not services.db_manager:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return services.db_manager


def get_cache_manager() -> CacheManager:
    """Dependency to get cache manager"""
    if not services.cache_manager:
        raise HTTPException(status_code=503, detail="Cache not initialized")
    return services.cache_manager


# ==============================================
# LIFECYCLE MANAGEMENT
# ==============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    await services.initialize()
    yield
    # Shutdown
    await services.shutdown()


# ==============================================
# FASTAPI APPLICATION
# ==============================================

app = FastAPI(
    title="Chef Bot - Recipe Service",
    description="Recipe management service for Chef Bot Telegram assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================
# ROUTES
# ==============================================

@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "service": "Recipe Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(
    themealdb: TheMealDBClient = Depends(get_themealdb_client),
    db: DatabaseManager = Depends(get_db_manager),
    cache: CacheManager = Depends(get_cache_manager)
):
    """
    Health check endpoint
    Verifies all dependencies are working
    """
    health_status = {
        "status": "healthy",
        "service": "recipe-service",
        "database": "unknown",
        "cache": "unknown",
        "external_api": "unknown"
    }
    
    # Check database
    try:
        await db.check_connection()
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["database"] = "disconnected"
        health_status["status"] = "degraded"
    
    # Check cache
    try:
        await cache.ping()
        health_status["cache"] = "connected"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        health_status["cache"] = "disconnected"
        health_status["status"] = "degraded"
    
    # Check external API
    try:
        # Try to get a random recipe as health check
        test_recipe = await themealdb.get_random_recipe()
        health_status["external_api"] = "available" if test_recipe else "unavailable"
    except Exception as e:
        logger.error(f"External API health check failed: {e}")
        health_status["external_api"] = "unavailable"
        health_status["status"] = "degraded"
    
    return health_status


@app.post("/api/v1/recipes/search", response_model=RecipeListResponse)
async def search_recipes(
    request: RecipeSearchRequest,
    themealdb: TheMealDBClient = Depends(get_themealdb_client),
    cache: CacheManager = Depends(get_cache_manager),
    db: DatabaseManager = Depends(get_db_manager)
):
    """
    Search recipes by ingredients
    
    - **ingredients**: List of 1-3 ingredients to search for
    - **dietary_filter**: Optional filter (vegetarian, vegan, gluten_free)
    - **user_id**: Optional user ID to save search history
    """
    try:
        logger.info(f"Searching recipes with ingredients: {request.ingredients}")
        
        # Generate cache key
        cache_key = f"search:{':'.join(sorted(request.ingredients))}:{request.dietary_filter or 'none'}"
        
        # Try to get from cache first
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.info("Returning cached results")
            return cached_result
        
        # Search by first ingredient (TheMealDB limitation)
        # TODO: Implement multi-ingredient filtering
        recipes = await themealdb.search_by_ingredient(request.ingredients[0])
        
        # Apply dietary filter if specified
        if request.dietary_filter and request.dietary_filter != "none":
            recipes = [r for r in recipes if request.dietary_filter.lower() in [t.lower() for t in r.tags]]
        
        # Limit results to 10
        recipes = recipes[:10]
        
        # Convert to response format
        recipe_responses = [
            RecipeResponse(
                id=str(recipe.id),
                name=recipe.name,
                category=recipe.category,
                area=recipe.area,
                instructions=recipe.instructions,
                image_url=recipe.image_url,
                video_url=recipe.video_url,
                ingredients=[{"name": ing.name, "measure": ing.measure} for ing in recipe.ingredients],
                tags=recipe.tags
            )
            for recipe in recipes
        ]
        
        result = RecipeListResponse(recipes=recipe_responses, count=len(recipe_responses))
        
        # Cache the result for 1 hour
        await cache.set(cache_key, result.model_dump(), ttl=3600)
        
        # Save search history if user_id provided
        if request.user_id:
            try:
                await db.save_search_history(
                    user_id=request.user_id,
                    ingredients=request.ingredients,
                    results_count=len(recipes)
                )
            except Exception as e:
                logger.warning(f"Failed to save search history: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching recipes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search recipes: {str(e)}")


@app.get("/api/v1/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: str,
    themealdb: TheMealDBClient = Depends(get_themealdb_client),
    cache: CacheManager = Depends(get_cache_manager)
):
    """
    Get recipe by ID
    
    - **recipe_id**: TheMealDB recipe ID
    """
    try:
        logger.info(f"Getting recipe: {recipe_id}")
        
        # Try cache first
        cache_key = f"recipe:{recipe_id}"
        cached_recipe = await cache.get(cache_key)
        if cached_recipe:
            logger.info("Returning cached recipe")
            return cached_recipe
        
        # Get from API
        recipe = await themealdb.get_recipe_by_id(recipe_id)
        
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # Convert to response
        recipe_response = RecipeResponse(
            id=str(recipe.id),
            name=recipe.name,
            category=recipe.category,
            area=recipe.area,
            instructions=recipe.instructions,
            image_url=recipe.image_url,
            video_url=recipe.video_url,
            ingredients=[{"name": ing.name, "measure": ing.measure} for ing in recipe.ingredients],
            tags=recipe.tags
        )
        
        # Cache for 7 days
        await cache.set(cache_key, recipe_response.model_dump(), ttl=604800)
        
        return recipe_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recipe: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recipe: {str(e)}")


@app.get("/api/v1/recipes/random", response_model=RecipeResponse)
async def get_random_recipe(
    themealdb: TheMealDBClient = Depends(get_themealdb_client)
):
    """
    Get a random recipe
    Used for recommendations
    """
    try:
        logger.info("Getting random recipe")
        
        recipe = await themealdb.get_random_recipe()
        
        if not recipe:
            raise HTTPException(status_code=404, detail="No recipe found")
        
        return RecipeResponse(
            id=str(recipe.id),
            name=recipe.name,
            category=recipe.category,
            area=recipe.area,
            instructions=recipe.instructions,
            image_url=recipe.image_url,
            video_url=recipe.video_url,
            ingredients=[{"name": ing.name, "measure": ing.measure} for ing in recipe.ingredients],
            tags=recipe.tags
        )
        
    except Exception as e:
        logger.error(f"Error getting random recipe: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get random recipe: {str(e)}")


@app.get("/api/v1/users/{user_id}/favorites", response_model=List[dict])
async def get_user_favorites(
    user_id: str,
    db: DatabaseManager = Depends(get_db_manager)
):
    """
    Get user's favorite recipes
    
    - **user_id**: Telegram user ID
    """
    try:
        logger.info(f"Getting favorites for user: {user_id}")
        favorites = await db.get_user_favorites(user_id)
        return favorites
    except Exception as e:
        logger.error(f"Error getting favorites: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get favorites: {str(e)}")


@app.post("/api/v1/users/{user_id}/favorites/{recipe_id}")
async def add_favorite(
    user_id: str,
    recipe_id: str,
    recipe_name: str,
    recipe_image: Optional[str] = None,
    db: DatabaseManager = Depends(get_db_manager)
):
    """
    Add recipe to favorites
    
    - **user_id**: Telegram user ID
    - **recipe_id**: Recipe ID
    - **recipe_name**: Recipe name
    - **recipe_image**: Optional recipe image URL
    """
    try:
        logger.info(f"Adding recipe {recipe_id} to favorites for user {user_id}")
        success = await db.add_favorite(user_id, recipe_id, recipe_name, recipe_image or "")
        
        if not success:
            raise HTTPException(status_code=400, detail="Cannot add favorite. Limit of 10 reached.")
        
        return {"message": "Recipe added to favorites", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding favorite: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add favorite: {str(e)}")


@app.delete("/api/v1/users/{user_id}/favorites/{recipe_id}")
async def remove_favorite(
    user_id: str,
    recipe_id: str,
    db: DatabaseManager = Depends(get_db_manager)
):
    """
    Remove recipe from favorites
    
    - **user_id**: Telegram user ID
    - **recipe_id**: Recipe ID to remove
    """
    try:
        logger.info(f"Removing recipe {recipe_id} from favorites for user {user_id}")
        success = await db.remove_favorite(user_id, recipe_id)
        
        if success:
            return {"message": "Recipe removed from favorites", "success": True}
        else:
            raise HTTPException(status_code=404, detail="Favorite not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing favorite: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remove favorite: {str(e)}")


@app.get("/api/v1/users/{user_id}/filter")
async def get_user_filter(
    user_id: str,
    db: DatabaseManager = Depends(get_db_manager)
):
    """
    Get user's dietary filter
    
    - **user_id**: Telegram user ID
    """
    try:
        filter_value = await db.get_user_filter(user_id)
        return {"user_id": user_id, "dietary_filter": filter_value}
    except Exception as e:
        logger.error(f"Error getting user filter: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user filter: {str(e)}")


@app.put("/api/v1/users/{user_id}/filter")
async def update_user_filter(
    user_id: str,
    dietary_filter: str,
    db: DatabaseManager = Depends(get_db_manager)
):
    """
    Update user's dietary filter
    
    - **user_id**: Telegram user ID
    - **dietary_filter**: New filter value (none, vegetarian, vegan, gluten_free)
    """
    try:
        logger.info(f"Updating filter to {dietary_filter} for user {user_id}")
        success = await db.update_user_filter(user_id, dietary_filter)
        
        if success:
            return {"message": "Filter updated successfully", "dietary_filter": dietary_filter}
        else:
            raise HTTPException(status_code=400, detail="Failed to update filter")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user filter: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update filter: {str(e)}")


@app.get("/api/v1/users/{user_id}/recommendations", response_model=RecipeListResponse)
async def get_recommendations(
    user_id: str,
    themealdb: TheMealDBClient = Depends(get_themealdb_client),
    db: DatabaseManager = Depends(get_db_manager)
):
    """
    Get recipe recommendations for user based on history
    
    - **user_id**: Telegram user ID
    """
    try:
        logger.info(f"Getting recommendations for user: {user_id}")
        
        # Get user's dietary filter
        dietary_filter = await db.get_user_filter(user_id)
        
        # Get 3 random recipes (simple recommendation for now)
        # TODO: Improve with ML-based recommendations
        recipes = []
        for _ in range(3):
            recipe = await themealdb.get_random_recipe()
            if recipe and recipe not in recipes:
                recipes.append(recipe)
        
        # Convert to response format
        recipe_responses = [
            RecipeResponse(
                id=str(recipe.id),
                name=recipe.name,
                category=recipe.category,
                area=recipe.area,
                instructions=recipe.instructions,
                image_url=recipe.image_url,
                video_url=recipe.video_url,
                ingredients=[{"name": ing.name, "measure": ing.measure} for ing in recipe.ingredients],
                tags=recipe.tags
            )
            for recipe in recipes
        ]
        
        return RecipeListResponse(recipes=recipe_responses, count=len(recipe_responses))
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


# ==============================================
# ERROR HANDLERS
# ==============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# ==============================================
# MAIN
# ==============================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "3001"))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("NODE_ENV") != "production",
        log_level="info"
    )
