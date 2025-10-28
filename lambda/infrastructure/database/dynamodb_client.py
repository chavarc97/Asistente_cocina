import boto3
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError


class DynamoDBClient:
    def __init__(self, region_name: str = 'us-east-1'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.client = boto3.client('dynamodb', region_name=region_name)

    def get_table(self, table_name: str):
        return self.dynamodb.Table(table_name)

    def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict]:
        try:
            table = self.get_table(table_name)
            response = table.get_item(Key=key)
            return response.get('Item')
        except ClientError:
            return None

    def put_item(self, table_name: str, item: Dict[str, Any]) -> bool:
        try:
            table = self.get_table(table_name)
            table.put_item(Item=item)
            return True
        except ClientError:
            return False

    def update_item(self, table_name: str, key: Dict[str, Any],
                   update_expression: str, expression_values: Dict[str, Any]) -> bool:
        try:
            table = self.get_table(table_name)
            table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            return True
        except ClientError:
            return False

    def delete_item(self, table_name: str, key: Dict[str, Any]) -> bool:
        try:
            table = self.get_table(table_name)
            table.delete_item(Key=key)
            return True
        except ClientError:
            return False

    def query(self, table_name: str, key_condition_expression,
             expression_attribute_values: Dict[str, Any]):
        try:
            table = self.get_table(table_name)
            response = table.query(
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return response.get('Items', [])
        except ClientError:
            return []

    def scan(self, table_name: str, filter_expression=None):
        try:
            table = self.get_table(table_name)
            if filter_expression:
                response = table.scan(FilterExpression=filter_expression)
            else:
                response = table.scan()
            return response.get('Items', [])
        except ClientError:
            return []
