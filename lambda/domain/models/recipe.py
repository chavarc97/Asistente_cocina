from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class Ingredient:
    name: str
    amount: float
    unit: str
    original: str


@dataclass
class Step:
    number: int
    instruction: str
    duration: Optional[int] = None


@dataclass
class Recipe:
    recipe_id: str
    title: str
    ingredients: List[Ingredient]
    steps: List[Step]
    ready_in_minutes: int
    servings: int
    image_url: Optional[str] = None
    dietary_info: List[str] = field(default_factory=list)
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    source: Optional[str] = None
    cached_at: Optional[datetime] = None

    def adjust_servings(self, target_servings: int):
        ratio = target_servings / self.servings
        for ingredient in self.ingredients:
            ingredient.amount *= ratio
        self.servings = target_servings

    def get_total_duration(self) -> int:
        return sum(step.duration for step in self.steps if step.duration)

    def matches_restrictions(self, restrictions: List[str]) -> bool:
        return all(restriction in self.dietary_info for restriction in restrictions)

    def to_dict(self) -> Dict:
        return {
            'recipeId': self.recipe_id,
            'title': self.title,
            'ingredients': [
                {
                    'name': ing.name,
                    'amount': ing.amount,
                    'unit': ing.unit,
                    'original': ing.original
                } for ing in self.ingredients
            ],
            'steps': [
                {
                    'number': step.number,
                    'instruction': step.instruction,
                    'duration': step.duration
                } for step in self.steps
            ],
            'readyInMinutes': self.ready_in_minutes,
            'servings': self.servings,
            'imageUrl': self.image_url,
            'dietaryInfo': self.dietary_info,
            'cuisine': self.cuisine,
            'difficulty': self.difficulty,
            'source': self.source,
            'cachedAt': self.cached_at.isoformat() if self.cached_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            recipe_id=data['recipeId'],
            title=data['title'],
            ingredients=[
                Ingredient(
                    name=ing['name'],
                    amount=ing['amount'],
                    unit=ing['unit'],
                    original=ing['original']
                ) for ing in data['ingredients']
            ],
            steps=[
                Step(
                    number=step['number'],
                    instruction=step['instruction'],
                    duration=step.get('duration')
                ) for step in data['steps']
            ],
            ready_in_minutes=data['readyInMinutes'],
            servings=data['servings'],
            image_url=data.get('imageUrl'),
            dietary_info=data.get('dietaryInfo', []),
            cuisine=data.get('cuisine'),
            difficulty=data.get('difficulty'),
            source=data.get('source'),
            cached_at=datetime.fromisoformat(data['cachedAt']) if data.get('cachedAt') else None
        )
