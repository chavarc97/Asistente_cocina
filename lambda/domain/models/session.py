from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class SessionState(Enum):
    IDLE = "idle"
    SEARCHING = "searching"
    RECIPE_SELECTED = "recipe_selected"
    COOKING = "cooking"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class Timer:
    name: str
    duration_seconds: int
    started_at: datetime


@dataclass
class CookingSession:
    session_id: str
    user_id: str
    recipe_id: str
    state: SessionState = SessionState.IDLE
    current_step: int = 0
    timers: List[Timer] = field(default_factory=list)
    started_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

    def advance_step(self):
        self.current_step += 1
        self.updated_at = datetime.utcnow()

    def go_back(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.updated_at = datetime.utcnow()

    def pause(self):
        self.state = SessionState.PAUSED
        self.updated_at = datetime.utcnow()

    def resume(self):
        self.state = SessionState.COOKING
        self.updated_at = datetime.utcnow()

    def complete(self):
        self.state = SessionState.COMPLETED
        self.updated_at = datetime.utcnow()

    def add_timer(self, name: str, duration_seconds: int):
        timer = Timer(name, duration_seconds, datetime.utcnow())
        self.timers.append(timer)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        return {
            'sessionId': self.session_id,
            'userId': self.user_id,
            'recipeId': self.recipe_id,
            'state': self.state.value,
            'currentStep': self.current_step,
            'timers': [
                {
                    'name': timer.name,
                    'durationSeconds': timer.duration_seconds,
                    'startedAt': timer.started_at.isoformat()
                } for timer in self.timers
            ],
            'startedAt': self.started_at.isoformat() if self.started_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            session_id=data['sessionId'],
            user_id=data['userId'],
            recipe_id=data['recipeId'],
            state=SessionState(data.get('state', 'idle')),
            current_step=data.get('currentStep', 0),
            timers=[
                Timer(
                    name=t['name'],
                    duration_seconds=t['durationSeconds'],
                    started_at=datetime.fromisoformat(t['startedAt'])
                ) for t in data.get('timers', [])
            ],
            started_at=datetime.fromisoformat(data['startedAt']) if data.get('startedAt') else None,
            updated_at=datetime.fromisoformat(data['updatedAt']) if data.get('updatedAt') else None
        )
