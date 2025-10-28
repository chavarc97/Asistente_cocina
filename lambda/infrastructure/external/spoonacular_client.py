import requests
from typing import List, Optional, Dict
from lambda.domain.models import Recipe, Ingredient, Step
from datetime import datetime


class SpoonacularClient:
    BASE_URL = "https://api.spoonacular.com"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def search_by_ingredients(self, ingredients: List[str], number: int = 5,
                             diet: Optional[str] = None) -> List[Dict]:
        endpoint = f"{self.BASE_URL}/recipes/findByIngredients"
        params = {
            'apiKey': self.api_key,
            'ingredients': ','.join(ingredients),
            'number': number,
            'ranking': 2
        }

        if diet:
            params['diet'] = diet

        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def get_recipe_information(self, recipe_id: str) -> Optional[Recipe]:
        endpoint = f"{self.BASE_URL}/recipes/{recipe_id}/information"
        params = {
            'apiKey': self.api_key,
            'includeNutrition': False
        }

        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()

        return self._parse_recipe(data)

    def search_complex(self, query: str = "", cuisine: str = "",
                      diet: str = "", max_ready_time: int = None,
                      number: int = 5) -> List[Dict]:
        endpoint = f"{self.BASE_URL}/recipes/complexSearch"
        params = {
            'apiKey': self.api_key,
            'query': query,
            'number': number,
            'addRecipeInformation': True
        }

        if cuisine:
            params['cuisine'] = cuisine
        if diet:
            params['diet'] = diet
        if max_ready_time:
            params['maxReadyTime'] = max_ready_time

        response = self.session.get(endpoint, params=params)
        response.raise_for_status()
        return response.json().get('results', [])

    def _parse_recipe(self, data: Dict) -> Recipe:
        ingredients = [
            Ingredient(
                name=ing.get('name', ''),
                amount=ing.get('amount', 0),
                unit=ing.get('unit', ''),
                original=ing.get('original', '')
            ) for ing in data.get('extendedIngredients', [])
        ]

        steps = []
        analyzed_instructions = data.get('analyzedInstructions', [])
        if analyzed_instructions:
            for step_data in analyzed_instructions[0].get('steps', []):
                steps.append(
                    Step(
                        number=step_data.get('number', 0),
                        instruction=step_data.get('step', ''),
                        duration=None
                    )
                )

        dietary_info = []
        if data.get('vegetarian'):
            dietary_info.append('vegetarian')
        if data.get('vegan'):
            dietary_info.append('vegan')
        if data.get('glutenFree'):
            dietary_info.append('gluten-free')

        return Recipe(
            recipe_id=str(data['id']),
            title=data.get('title', ''),
            ingredients=ingredients,
            steps=steps,
            ready_in_minutes=data.get('readyInMinutes', 0),
            servings=data.get('servings', 1),
            image_url=data.get('image'),
            dietary_info=dietary_info,
            cuisine=data.get('cuisines', [None])[0] if data.get('cuisines') else None,
            difficulty=None,
            source='spoonacular',
            cached_at=datetime.utcnow()
        )
