from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


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

    def update_preferences(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.last_updated = datetime.utcnow()

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
