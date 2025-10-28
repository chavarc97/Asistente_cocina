from typing import Optional
from lambda.domain.models import User
from lambda.domain.repositories import IUserRepository
from lambda.infrastructure.database.dynamodb_client import DynamoDBClient


class DynamoDBUserRepository(IUserRepository):
    def __init__(self, client: DynamoDBClient, table_name: str = 'UserProfiles'):
        self.client = client
        self.table_name = table_name

    def get_by_id(self, user_id: str) -> Optional[User]:
        item = self.client.get_item(
            self.table_name,
            {'userId': user_id}
        )
        if item:
            return User.from_dict(item)
        return None

    def save(self, user: User) -> None:
        self.client.put_item(self.table_name, user.to_dict())

    def update(self, user: User) -> None:
        self.save(user)

    def delete(self, user_id: str) -> None:
        self.client.delete_item(
            self.table_name,
            {'userId': user_id}
        )

    def exists(self, user_id: str) -> bool:
        item = self.client.get_item(
            self.table_name,
            {'userId': user_id}
        )
        return item is not None
