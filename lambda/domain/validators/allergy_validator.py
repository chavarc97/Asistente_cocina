from typing import List, Set


class AllergyValidator:
    COMMON_ALLERGENS: Set[str] = {
        'cacahuetes', 'nueces', 'leche', 'huevos', 'pescado',
        'mariscos', 'trigo', 'soja', 'ajonjolí', 'mostaza',
        'apio', 'sulfitos', 'gluten', 'lactosa'
    }

    ALLERGEN_SYNONYMS = {
        'maní': 'cacahuetes',
        'cacahuate': 'cacahuetes',
        'frutos secos': 'nueces',
        'almendras': 'nueces',
        'lácteos': 'leche',
        'huevo': 'huevos',
        'marisco': 'mariscos',
        'camarones': 'mariscos',
        'gluten': 'trigo',
        'harina': 'trigo',
        'soya': 'soja',
        'sésamo': 'ajonjolí'
    }

    @classmethod
    def normalize_allergen(cls, allergen: str) -> str:
        allergen_lower = allergen.lower().strip()
        return cls.ALLERGEN_SYNONYMS.get(allergen_lower, allergen_lower)

    @classmethod
    def validate_allergen(cls, allergen: str) -> bool:
        normalized = cls.normalize_allergen(allergen)
        return normalized in cls.COMMON_ALLERGENS

    @classmethod
    def validate_allergies(cls, allergies: List[str]) -> List[str]:
        if not allergies:
            return []

        validated = []
        for allergen in allergies:
            normalized = cls.normalize_allergen(allergen)
            if normalized and normalized not in validated:
                validated.append(normalized)

        return validated

    @classmethod
    def is_duplicate(cls, allergen: str, existing_allergies: List[str]) -> bool:
        normalized = cls.normalize_allergen(allergen)
        normalized_existing = [cls.normalize_allergen(a) for a in existing_allergies]
        return normalized in normalized_existing
