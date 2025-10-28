from typing import Optional
from boto3.dynamodb.conditions import Key, Attr
from lambda.domain.models import CookingSession, SessionState
from lambda.domain.repositories import ISessionRepository
from lambda.infrastructure.database.dynamodb_client import DynamoDBClient


class DynamoDBSessionRepository(ISessionRepository):
    def __init__(self, client: DynamoDBClient, table_name: str = 'CookingSessions'):
        self.client = client
        self.table_name = table_name

    def get_by_id(self, session_id: str) -> Optional[CookingSession]:
        item = self.client.get_item(
            self.table_name,
            {'sessionId': session_id}
        )
        if item:
            return CookingSession.from_dict(item)
        return None

    def get_active_session(self, user_id: str) -> Optional[CookingSession]:
        items = self.client.query(
            self.table_name,
            Key('userId').eq(user_id),
            {':userId': user_id}
        )

        for item in items:
            session = CookingSession.from_dict(item)
            if session.state in [SessionState.COOKING, SessionState.PAUSED]:
                return session
        return None

    def save(self, session: CookingSession) -> None:
        self.client.put_item(self.table_name, session.to_dict())

    def update(self, session: CookingSession) -> None:
        self.save(session)

    def delete(self, session_id: str) -> None:
        self.client.delete_item(
            self.table_name,
            {'sessionId': session_id}
        )
