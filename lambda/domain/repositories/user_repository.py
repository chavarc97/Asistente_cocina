from abc import ABC, abstractmethod
from typing import Optional
from lambda.domain.models import User


class IUserRepository(ABC):

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def update(self, user: User) -> None:
        pass

    @abstractmethod
    def delete(self, user_id: str) -> None:
        pass

    @abstractmethod
    def exists(self, user_id: str) -> bool:
        pass
