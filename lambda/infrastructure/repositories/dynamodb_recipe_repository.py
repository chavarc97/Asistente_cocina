from typing import Optional, List
from boto3.dynamodb.conditions import Key
from lambda.domain.models import Recipe
from lambda.domain.repositories import IRecipeRepository
from lambda.infrastructure.database.dynamodb_client import DynamoDBClient


class DynamoDBRecipeRepository(IRecipeRepository):
    def __init__(self, client: DynamoDBClient,
                 cache_table: str = 'RecipeCache',
                 favorites_table: str = 'FavoriteRecipes'):
        self.client = client
        self.cache_table = cache_table
        self.favorites_table = favorites_table

    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        item = self.client.get_item(
            self.cache_table,
            {'recipeId': recipe_id}
        )
        if item:
            return Recipe.from_dict(item)
        return None

    def save(self, recipe: Recipe) -> None:
        self.client.put_item(self.cache_table, recipe.to_dict())

    def get_user_favorites(self, user_id: str) -> List[Recipe]:
        items = self.client.query(
            self.favorites_table,
            Key('userId').eq(user_id),
            {':userId': user_id}
        )
        recipes = []
        for item in items:
            recipe = self.get_by_id(item['recipeId'])
            if recipe:
                recipes.append(recipe)
        return recipes

    def add_to_favorites(self, user_id: str, recipe_id: str) -> None:
        from datetime import datetime
        self.client.put_item(
            self.favorites_table,
            {
                'userId': user_id,
                'recipeId': recipe_id,
                'addedAt': datetime.utcnow().isoformat()
            }
        )

    def remove_from_favorites(self, user_id: str, recipe_id: str) -> None:
        self.client.delete_item(
            self.favorites_table,
            {'userId': user_id, 'recipeId': recipe_id}
        )

    def is_favorite(self, user_id: str, recipe_id: str) -> bool:
        item = self.client.get_item(
            self.favorites_table,
            {'userId': user_id, 'recipeId': recipe_id}
        )
        return item is not None
