from typing import Optional, Dict
from lambda.domain.models import User, SkillLevel
from lambda.domain.repositories import IUserRepository


class UserService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def get_or_create_user(self, user_id: str) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            user = User(user_id=user_id)
            self.user_repository.save(user)
        return user

    def update_dietary_restrictions(self, user_id: str, restrictions: list) -> User:
        user = self.get_or_create_user(user_id)
        user.update_preferences(dietary_restrictions=restrictions)
        self.user_repository.update(user)
        return user

    def update_skill_level(self, user_id: str, skill_level: str) -> User:
        user = self.get_or_create_user(user_id)
        user.update_preferences(skill_level=SkillLevel(skill_level))
        self.user_repository.update(user)
        return user

    def update_servings(self, user_id: str, servings: int) -> User:
        user = self.get_or_create_user(user_id)
        user.update_preferences(servings=servings)
        self.user_repository.update(user)
        return user

    def update_preferences(self, user_id: str, preferences: Dict) -> User:
        user = self.get_or_create_user(user_id)
        user.update_preferences(**preferences)
        self.user_repository.update(user)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.user_repository.get_by_id(user_id)
