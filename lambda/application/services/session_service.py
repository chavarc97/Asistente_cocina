from typing import Optional
from uuid import uuid4
from lambda.domain.models import CookingSession, SessionState, Recipe
from lambda.domain.repositories import ISessionRepository


class SessionService:
    def __init__(self, session_repository: ISessionRepository):
        self.session_repository = session_repository

    def create_session(self, user_id: str, recipe_id: str) -> CookingSession:
        session_id = str(uuid4())
        session = CookingSession(
            session_id=session_id,
            user_id=user_id,
            recipe_id=recipe_id,
            state=SessionState.RECIPE_SELECTED
        )
        self.session_repository.save(session)
        return session

    def get_active_session(self, user_id: str) -> Optional[CookingSession]:
        return self.session_repository.get_active_session(user_id)

    def start_cooking(self, session_id: str) -> CookingSession:
        session = self.session_repository.get_by_id(session_id)
        if session:
            session.state = SessionState.COOKING
            session.current_step = 0
            self.session_repository.update(session)
        return session

    def next_step(self, session_id: str) -> Optional[int]:
        session = self.session_repository.get_by_id(session_id)
        if session:
            session.advance_step()
            self.session_repository.update(session)
            return session.current_step
        return None

    def previous_step(self, session_id: str) -> Optional[int]:
        session = self.session_repository.get_by_id(session_id)
        if session:
            session.go_back()
            self.session_repository.update(session)
            return session.current_step
        return None

    def pause_session(self, session_id: str) -> None:
        session = self.session_repository.get_by_id(session_id)
        if session:
            session.pause()
            self.session_repository.update(session)

    def resume_session(self, session_id: str) -> None:
        session = self.session_repository.get_by_id(session_id)
        if session:
            session.resume()
            self.session_repository.update(session)

    def complete_session(self, session_id: str) -> None:
        session = self.session_repository.get_by_id(session_id)
        if session:
            session.complete()
            self.session_repository.update(session)

    def add_timer(self, session_id: str, name: str, duration: int) -> None:
        session = self.session_repository.get_by_id(session_id)
        if session:
            session.add_timer(name, duration)
            self.session_repository.update(session)

    def get_current_step(self, session_id: str, recipe: Recipe) -> Optional[str]:
        session = self.session_repository.get_by_id(session_id)
        if session and session.current_step < len(recipe.steps):
            return recipe.steps[session.current_step].instruction
        return None
