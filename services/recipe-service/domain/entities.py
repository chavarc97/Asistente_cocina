# ==============================================
# DOMAIN ENTITIES - RECIPE SERVICE
# Demuestra: Domain-Driven Design, Entity Pattern
# ==============================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid


class DietaryFilter(Enum):
    """Filtros dietéticos disponibles"""
    NONE = "none"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"


@dataclass(frozen=True)
class RecipeId:
    """Value Object para ID de receta (de TheMealDB)"""
    value: str
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class UserId:
    """Value Object para ID de usuario"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            object.__setattr__(self, 'value', str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass
class Ingredient:
    """
    Value Object para ingrediente
    Representa un ingrediente con su cantidad
    """
    name: str
    measure: Optional[str] = None
    
    def __str__(self) -> str:
        if self.measure:
            return f"{self.measure} {self.name}"
        return self.name


@dataclass
class RecipeStep:
    """Value Object para paso de receta"""
    number: int
    instruction: str
    
    def __str__(self) -> str:
        return f"Paso {self.number}: {self.instruction}"


@dataclass
class Recipe:
    """
    Entity: Receta
    Representa una receta completa del sistema
    """
    id: RecipeId
    name: str
    category: str
    area: str  # Origen/cocina (Mexican, Italian, etc.)
    instructions: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    ingredients: List[Ingredient] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    source: Optional[str] = None  # URL fuente original
    
    @property
    def steps(self) -> List[RecipeStep]:
        """Convierte instrucciones en pasos numerados"""
        if not self.instructions:
            return []
        
        # Dividir por saltos de línea o puntos
        raw_steps = [s.strip() for s in self.instructions.split('\n') if s.strip()]
        
        # Si no hay saltos de línea, intentar dividir por puntos
        if len(raw_steps) == 1:
            raw_steps = [s.strip() for s in self.instructions.split('.') if s.strip()]
        
        return [
            RecipeStep(number=i+1, instruction=step) 
            for i, step in enumerate(raw_steps)
        ]
    
    @property
    def total_steps(self) -> int:
        return len(self.steps)
    
    @property
    def ingredients_list(self) -> List[str]:
        """Lista de ingredientes como strings"""
        return [str(ing) for ing in self.ingredients]
    
    def get_step(self, step_number: int) -> Optional[RecipeStep]:
        """Obtiene un paso específico"""
        steps = self.steps
        if 1 <= step_number <= len(steps):
            return steps[step_number - 1]
        return None
    
    def is_vegetarian(self) -> bool:
        """Verifica si la receta es vegetariana basándose en categoría"""
        vegetarian_categories = ['vegetarian', 'vegan', 'side', 'dessert', 'breakfast']
        return self.category.lower() in vegetarian_categories
    
    def matches_filter(self, dietary_filter: DietaryFilter) -> bool:
        """Verifica si la receta cumple con el filtro dietético"""
        if dietary_filter == DietaryFilter.NONE:
            return True
        
        if dietary_filter == DietaryFilter.VEGETARIAN:
            return self.is_vegetarian()
        
        # Para vegano y sin gluten, necesitaríamos análisis más profundo
        # Por ahora, retornamos True si la categoría coincide
        if dietary_filter == DietaryFilter.VEGAN:
            return 'vegan' in self.category.lower()
        
        if dietary_filter == DietaryFilter.GLUTEN_FREE:
            # Simplificación: excluir pastas y panes
            gluten_ingredients = ['flour', 'bread', 'pasta', 'wheat']
            return not any(
                any(g in ing.name.lower() for g in gluten_ingredients)
                for ing in self.ingredients
            )
        
        return True
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización"""
        return {
            'id': str(self.id),
            'name': self.name,
            'category': self.category,
            'area': self.area,
            'instructions': self.instructions,
            'image_url': self.image_url,
            'video_url': self.video_url,
            'ingredients': [
                {'name': ing.name, 'measure': ing.measure}
                for ing in self.ingredients
            ],
            'tags': self.tags,
            'source': self.source,
            'total_steps': self.total_steps
        }
    
    @classmethod
    def from_themealdb(cls, data: dict) -> 'Recipe':
        """
        Factory method para crear Recipe desde respuesta de TheMealDB
        """
        # Extraer ingredientes (TheMealDB tiene strIngredient1-20)
        ingredients = []
        for i in range(1, 21):
            ing_name = data.get(f'strIngredient{i}')
            ing_measure = data.get(f'strMeasure{i}')
            
            if ing_name and ing_name.strip():
                ingredients.append(Ingredient(
                    name=ing_name.strip(),
                    measure=ing_measure.strip() if ing_measure else None
                ))
        
        # Extraer tags
        tags = []
        if data.get('strTags'):
            tags = [t.strip() for t in data['strTags'].split(',')]
        
        return cls(
            id=RecipeId(data['idMeal']),
            name=data.get('strMeal', ''),
            category=data.get('strCategory', ''),
            area=data.get('strArea', ''),
            instructions=data.get('strInstructions', ''),
            image_url=data.get('strMealThumb'),
            video_url=data.get('strYoutube'),
            ingredients=ingredients,
            tags=tags,
            source=data.get('strSource')
        )


@dataclass
class SearchResult:
    """Entity: Resultado de búsqueda"""
    recipes: List[Recipe]
    query: str
    ingredients: List[str]
    dietary_filter: DietaryFilter
    total_results: int
    searched_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            'recipes': [r.to_dict() for r in self.recipes],
            'query': self.query,
            'ingredients': self.ingredients,
            'dietary_filter': self.dietary_filter.value,
            'total_results': self.total_results,
            'searched_at': self.searched_at.isoformat()
        }