import boto3
from ask_sdk_dynamodb.adapter import DynamoDbAdapter
from typing import Optional


class AlexaDynamoDBPersistenceAdapter:
    def __init__(self, table_name: str = 'AlexaSessionAttributes', region_name: str = 'us-east-1'):
        self.table_name = table_name
        self.region_name = region_name
        self._adapter = None

    @property
    def adapter(self):
        if self._adapter is None:
            self._adapter = DynamoDbAdapter(
                table_name=self.table_name,
                partition_key_name='id',
                attribute_name='attributes',
                create_table=False,
                dynamodb_resource=boto3.resource('dynamodb', region_name=self.region_name)
            )
        return self._adapter

    def get_adapter(self):
        return self.adapter
