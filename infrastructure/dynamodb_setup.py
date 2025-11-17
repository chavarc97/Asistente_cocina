import boto3
from botocore.exceptions import ClientError


class DynamoDBSetup:
    def __init__(self, region_name='us-east-1'):
        self.dynamodb = boto3.client('dynamodb', region_name=region_name)

    def create_user_profiles_table(self):
        try:
            self.dynamodb.create_table(
                TableName='UserProfiles',
                KeySchema=[
                    {'AttributeName': 'userId', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'userId', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'Project', 'Value': 'ChefPersonal'},
                    {'Key': 'Environment', 'Value': 'Production'}
                ]
            )
            print("✓ UserProfiles table created successfully")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print("✓ UserProfiles table already exists")
            else:
                raise

    def create_recipe_cache_table(self):
        try:
            self.dynamodb.create_table(
                TableName='RecipeCache',
                KeySchema=[
                    {'AttributeName': 'recipeId', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'recipeId', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'expiresAt'
                },
                Tags=[
                    {'Key': 'Project', 'Value': 'ChefPersonal'},
                    {'Key': 'Environment', 'Value': 'Production'}
                ]
            )
            print("✓ RecipeCache table created successfully")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print("✓ RecipeCache table already exists")
            else:
                raise

    def create_favorite_recipes_table(self):
        try:
            self.dynamodb.create_table(
                TableName='FavoriteRecipes',
                KeySchema=[
                    {'AttributeName': 'userId', 'KeyType': 'HASH'},
                    {'AttributeName': 'recipeId', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'userId', 'AttributeType': 'S'},
                    {'AttributeName': 'recipeId', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'Project', 'Value': 'ChefPersonal'},
                    {'Key': 'Environment', 'Value': 'Production'}
                ]
            )
            print("✓ FavoriteRecipes table created successfully")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print("✓ FavoriteRecipes table already exists")
            else:
                raise

    def create_cooking_sessions_table(self):
        try:
            self.dynamodb.create_table(
                TableName='CookingSessions',
                KeySchema=[
                    {'AttributeName': 'sessionId', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'sessionId', 'AttributeType': 'S'},
                    {'AttributeName': 'userId', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'UserIdIndex',
                        'KeySchema': [
                            {'AttributeName': 'userId', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST',
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'expiresAt'
                },
                Tags=[
                    {'Key': 'Project', 'Value': 'ChefPersonal'},
                    {'Key': 'Environment', 'Value': 'Production'}
                ]
            )
            print("✓ CookingSessions table created successfully")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print("✓ CookingSessions table already exists")
            else:
                raise

    def create_user_history_table(self):
        try:
            self.dynamodb.create_table(
                TableName='UserHistory',
                KeySchema=[
                    {'AttributeName': 'userId', 'KeyType': 'HASH'},
                    {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'userId', 'AttributeType': 'S'},
                    {'AttributeName': 'timestamp', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'Project', 'Value': 'ChefPersonal'},
                    {'Key': 'Environment', 'Value': 'Production'}
                ]
            )
            print("✓ UserHistory table created successfully")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print("✓ UserHistory table already exists")
            else:
                raise

    def create_alexa_session_attributes_table(self):
        try:
            self.dynamodb.create_table(
                TableName='AlexaSessionAttributes',
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'ttl'
                },
                Tags=[
                    {'Key': 'Project', 'Value': 'ChefPersonal'},
                    {'Key': 'Environment', 'Value': 'Production'}
                ]
            )
            print("✓ AlexaSessionAttributes table created successfully")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print("✓ AlexaSessionAttributes table already exists")
            else:
                raise

    def setup_all_tables(self):
        print("\n=== Creating DynamoDB Tables ===\n")
        self.create_user_profiles_table()
        self.create_recipe_cache_table()
        self.create_favorite_recipes_table()
        self.create_cooking_sessions_table()
        self.create_user_history_table()
        self.create_alexa_session_attributes_table()
        print("\n=== Setup Complete ===\n")

    def delete_all_tables(self):
        tables = ['UserProfiles', 'RecipeCache', 'FavoriteRecipes',
                 'CookingSessions', 'UserHistory', 'AlexaSessionAttributes']
        print("\n=== Deleting DynamoDB Tables ===\n")
        for table_name in tables:
            try:
                self.dynamodb.delete_table(TableName=table_name)
                print(f"✓ {table_name} deleted successfully")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    print(f"✓ {table_name} doesn't exist")
                else:
                    print(f"✗ Error deleting {table_name}: {str(e)}")
        print("\n=== Deletion Complete ===\n")


if __name__ == "__main__":
    import sys

    setup = DynamoDBSetup()

    if len(sys.argv) > 1 and sys.argv[1] == 'delete':
        setup.delete_all_tables()
    else:
        setup.setup_all_tables()
