from typing import List, Set, Dict
from lambda.domain.validators.allergy_validator import AllergyValidator


class AllergyChecker:
    ALLERGEN_INGREDIENT_MAPPING = {
        'cacahuetes': ['peanut', 'cacahuete', 'cacahuate', 'maní', 'mani'],
        'nueces': ['walnut', 'almond', 'hazelnut', 'nut', 'nuez', 'almendra', 'avellana', 'pistachio'],
        'leche': ['milk', 'dairy', 'cheese', 'cream', 'butter', 'leche', 'lácteo', 'queso', 'crema', 'mantequilla'],
        'huevos': ['egg', 'huevo'],
        'pescado': ['fish', 'pescado', 'salmon', 'tuna', 'cod', 'atún', 'bacalao'],
        'mariscos': ['shellfish', 'shrimp', 'crab', 'lobster', 'marisco', 'camarón', 'cangrejo', 'langosta'],
        'trigo': ['wheat', 'flour', 'gluten', 'trigo', 'harina'],
        'soja': ['soy', 'soya', 'soja', 'tofu'],
        'ajonjolí': ['sesame', 'sésamo', 'ajonjolí'],
        'mostaza': ['mustard', 'mostaza'],
        'apio': ['celery', 'apio'],
        'sulfitos': ['sulfite', 'sulfito']
    }

    @classmethod
    def check_recipe_for_allergens(cls, ingredients: List[str], user_allergies: List[str]) -> Dict[str, List[str]]:
        found_allergens = {}

        normalized_allergies = [AllergyValidator.normalize_allergen(a) for a in user_allergies]

        for allergen in normalized_allergies:
            allergen_keywords = cls.ALLERGEN_INGREDIENT_MAPPING.get(allergen, [allergen])

            matching_ingredients = []
            for ingredient in ingredients:
                ingredient_lower = ingredient.lower()
                for keyword in allergen_keywords:
                    if keyword.lower() in ingredient_lower:
                        matching_ingredients.append(ingredient)
                        break

            if matching_ingredients:
                found_allergens[allergen] = matching_ingredients

        return found_allergens

    @classmethod
    def has_allergens(cls, ingredients: List[str], user_allergies: List[str]) -> bool:
        found = cls.check_recipe_for_allergens(ingredients, user_allergies)
        return len(found) > 0

    @classmethod
    def format_allergen_warning(cls, allergens_found: Dict[str, List[str]]) -> str:
        if not allergens_found:
            return ""

        warnings = []
        for allergen, ingredients in allergens_found.items():
            if len(ingredients) == 1:
                warnings.append(f"{allergen} en {ingredients[0]}")
            else:
                warnings.append(f"{allergen} en {', '.join(ingredients)}")

        if len(warnings) == 1:
            return f"ADVERTENCIA: Esta receta contiene {warnings[0]}"
        else:
            return f"ADVERTENCIA: Esta receta contiene {', '.join(warnings[:-1])} y {warnings[-1]}"
