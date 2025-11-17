from typing import List, Optional, Dict
from lambda.domain.models import Recipe, User
from lambda.domain.repositories import IRecipeRepository
from lambda.domain.services.allergy_checker import AllergyChecker


class RecipeService:
    def __init__(self, recipe_repository: IRecipeRepository):
        self.recipe_repository = recipe_repository

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        return self.recipe_repository.get_by_id(recipe_id)

    def cache_recipe(self, recipe: Recipe) -> None:
        self.recipe_repository.save(recipe)

    def get_favorites(self, user_id: str) -> List[Recipe]:
        return self.recipe_repository.get_user_favorites(user_id)

    def add_to_favorites(self, user_id: str, recipe_id: str) -> None:
        self.recipe_repository.add_to_favorites(user_id, recipe_id)

    def remove_from_favorites(self, user_id: str, recipe_id: str) -> None:
        self.recipe_repository.remove_from_favorites(user_id, recipe_id)

    def is_favorite(self, user_id: str, recipe_id: str) -> bool:
        return self.recipe_repository.is_favorite(user_id, recipe_id)

    def adjust_recipe_for_user(self, recipe: Recipe, user: User) -> Recipe:
        if recipe.servings != user.servings:
            recipe.adjust_servings(user.servings)
        return recipe

    def filter_by_restrictions(self, recipes: List[Recipe], restrictions: List[str]) -> List[Recipe]:
        return [r for r in recipes if r.matches_restrictions(restrictions)]

    def sort_by_difficulty(self, recipes: List[Recipe], skill_level: str) -> List[Recipe]:
        difficulty_order = {
            'beginner': ['easy', 'medium', 'hard'],
            'intermediate': ['medium', 'easy', 'hard'],
            'advanced': ['hard', 'medium', 'easy']
        }
        order = difficulty_order.get(skill_level, ['medium', 'easy', 'hard'])

        def sort_key(recipe: Recipe):
            try:
                return order.index(recipe.difficulty.lower() if recipe.difficulty else 'medium')
            except ValueError:
                return 1

        return sorted(recipes, key=sort_key)

    def check_allergens_in_recipe(self, recipe: Recipe, user_allergies: List[str]) -> Dict[str, List[str]]:
        ingredient_names = [ing.name for ing in recipe.ingredients]
        return AllergyChecker.check_recipe_for_allergens(ingredient_names, user_allergies)

    def is_recipe_safe(self, recipe: Recipe, user_allergies: List[str]) -> bool:
        allergens_found = self.check_allergens_in_recipe(recipe, user_allergies)
        return len(allergens_found) == 0

    def filter_by_allergies(self, recipes: List[Recipe], user_allergies: List[str]) -> List[Recipe]:
        return [r for r in recipes if self.is_recipe_safe(r, user_allergies)]
