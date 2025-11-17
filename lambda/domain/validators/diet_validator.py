from typing import Set


class DietValidator:
    VALID_DIETS: Set[str] = {
        'vegetariana', 'vegana', 'cetogénica', 'paleo',
        'sin gluten', 'mediterránea', 'ninguna'
    }

    DIET_SYNONYMS = {
        'vegetariano': 'vegetariana',
        'vegano': 'vegana',
        'keto': 'cetogénica',
        'cetogénico': 'cetogénica',
        'paleolítica': 'paleo',
        'gluten free': 'sin gluten',
        'celíaca': 'sin gluten',
        'celíaco': 'sin gluten',
        'mediterráneo': 'mediterránea',
        'normal': 'ninguna',
        'sin restricciones': 'ninguna'
    }

    @classmethod
    def normalize_diet(cls, diet: str) -> str:
        diet_lower = diet.lower().strip()
        return cls.DIET_SYNONYMS.get(diet_lower, diet_lower)

    @classmethod
    def validate_diet(cls, diet: str) -> bool:
        normalized = cls.normalize_diet(diet)
        return normalized in cls.VALID_DIETS
