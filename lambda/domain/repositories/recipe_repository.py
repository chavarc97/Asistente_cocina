from abc import ABC, abstractmethod
from typing import Optional, List
from lambda.domain.models import Recipe


class IRecipeRepository(ABC):

    @abstractmethod
    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        pass

    @abstractmethod
    def save(self, recipe: Recipe) -> None:
        pass

    @abstractmethod
    def get_user_favorites(self, user_id: str) -> List[Recipe]:
        pass

    @abstractmethod
    def add_to_favorites(self, user_id: str, recipe_id: str) -> None:
        pass

    @abstractmethod
    def remove_from_favorites(self, user_id: str, recipe_id: str) -> None:
        pass

    @abstractmethod
    def is_favorite(self, user_id: str, recipe_id: str) -> bool:
        pass
