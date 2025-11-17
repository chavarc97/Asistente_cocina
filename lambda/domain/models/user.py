from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum

from lambda.domain.validators.allergy_validator import AllergyValidator
from lambda.domain.validators.diet_validator import DietValidator


class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class User:
    user_id: str
    dietary_restrictions: List[str] = field(default_factory=list)
    skill_level: SkillLevel = SkillLevel.BEGINNER
    servings: int = 2
    allergies: List[str] = field(default_factory=list)
    preferred_cuisines: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()

        self.allergies = AllergyValidator.validate_allergies(self.allergies)
        self.dietary_restrictions = self._validate_dietary_restrictions(self.dietary_restrictions)

    def _validate_dietary_restrictions(self, restrictions: List[str]) -> List[str]:
        validated = []
        for restriction in restrictions:
            normalized = DietValidator.normalize_diet(restriction)
            if DietValidator.validate_diet(normalized) and normalized not in validated:
                validated.append(normalized)
        return validated

    def update_preferences(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.last_updated = datetime.utcnow()

    def add_allergy(self, allergen: str) -> bool:
        normalized = AllergyValidator.normalize_allergen(allergen)

        if AllergyValidator.is_duplicate(normalized, self.allergies):
            return False

        if AllergyValidator.validate_allergen(normalized):
            self.allergies.append(normalized)
            self.last_updated = datetime.utcnow()
            return True

        return False

    def remove_allergy(self, allergen: str) -> bool:
        normalized = AllergyValidator.normalize_allergen(allergen)
        normalized_allergies = [AllergyValidator.normalize_allergen(a) for a in self.allergies]

        if normalized in normalized_allergies:
            index = normalized_allergies.index(normalized)
            self.allergies.pop(index)
            self.last_updated = datetime.utcnow()
            return True

        return False

    def set_dietary_restriction(self, diet: str) -> bool:
        normalized = DietValidator.normalize_diet(diet)

        if DietValidator.validate_diet(normalized):
            self.dietary_restrictions = [normalized]
            self.last_updated = datetime.utcnow()
            return True

        return False

    def set_servings(self, servings: int) -> bool:
        if 1 <= servings <= 12:
            self.servings = servings
            self.last_updated = datetime.utcnow()
            return True

        return False

    def to_dict(self):
        return {
            'userId': self.user_id,
            'dietaryRestrictions': self.dietary_restrictions,
            'skillLevel': self.skill_level.value,
            'servings': self.servings,
            'allergies': self.allergies,
            'preferredCuisines': self.preferred_cuisines,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'lastUpdated': self.last_updated.isoformat() if self.last_updated else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            user_id=data['userId'],
            dietary_restrictions=data.get('dietaryRestrictions', []),
            skill_level=SkillLevel(data.get('skillLevel', 'beginner')),
            servings=data.get('servings', 2),
            allergies=data.get('allergies', []),
            preferred_cuisines=data.get('preferredCuisines', []),
            created_at=datetime.fromisoformat(data['createdAt']) if data.get('createdAt') else None,
            last_updated=datetime.fromisoformat(data['lastUpdated']) if data.get('lastUpdated') else None
        )
