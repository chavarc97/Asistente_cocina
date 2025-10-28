from abc import ABC, abstractmethod
from typing import Optional
from lambda.domain.models import CookingSession


class ISessionRepository(ABC):

    @abstractmethod
    def get_by_id(self, session_id: str) -> Optional[CookingSession]:
        pass

    @abstractmethod
    def get_active_session(self, user_id: str) -> Optional[CookingSession]:
        pass

    @abstractmethod
    def save(self, session: CookingSession) -> None:
        pass

    @abstractmethod
    def update(self, session: CookingSession) -> None:
        pass

    @abstractmethod
    def delete(self, session_id: str) -> None:
        pass
