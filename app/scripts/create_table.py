from botocore.client import BaseClient
from botocore.exceptions import ClientError
from pydantic_settings import BaseSettings

def create_table(db_client: BaseClient, settings:BaseSettings):
    try:
        db_client.describe_table(TableName=settings.db.USERS_TABLE_NAME)
        print(f"Table '{settings.db.USERS_TABLE_NAME}' already exists locally.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            if settings.ENV == 'development':            
                print(f"Table '{settings.db.USERS_TABLE_NAME}' not found locally. Creating it now...")
                
                db_client.create_table(
                    TableName=settings.db.USERS_TABLE_NAME,
                    BillingMode="PAY_PER_REQUEST",  # on-demand: no capacity planning,
                                         # safe default while traffic is
                                         # unpredictable. Revisit only if
                                         # steady high volume makes
                                         # provisioned + autoscaling cheaper.
                    AttributeDefinitions=[
                        # Only key attributes need declaring up front - DynamoDB is
                        # schemaless beyond PK/SK/index keys. Profile fields, post
                        # content, etc. are never listed here.
                        {"AttributeName": "PK", "AttributeType": "S"},
                        {"AttributeName": "SK", "AttributeType": "S"},
                        {"AttributeName": "GSI1PK", "AttributeType": "S"},
                        {"AttributeName": "GSI1SK", "AttributeType": "S"},
                    ],
                    KeySchema=[
                        {"AttributeName": "PK", "KeyType": "HASH"},
                        {"AttributeName": "SK", "KeyType": "RANGE"},
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            "IndexName": "GSI1",
                            "KeySchema": [
                                {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                                {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                            ],
                            # ALL: this is the sparse index on the post item itself
                            # (only public posts get GSI1PK/GSI1SK set), so a public
                            # timeline query returns full post data directly - no
                            # follow-up BatchGetItem, unlike the friend-feed pointers.
                            "Projection": {"ProjectionType": "ALL"},
                        }
                    ],
                    # Lets the async fan-out Lambda (Step 3's write path) react to
                    # new posts and write friend feed pointers in the background.
                    StreamSpecification={
                        "StreamEnabled": True,
                        "StreamViewType": "NEW_IMAGE",
                    },
                )

                # Local DynamoDB is instant, but keeping the waiter is a safe best practice
                waiter = db_client.get_waiter('table_exists')
                waiter.wait(TableName=settings.db.USERS_TABLE_NAME)
                print(f"Local table '{settings.db.USERS_TABLE_NAME}' is now active!")

                print(f"Adding TTL to local table '{settings.db.USERS_TABLE_NAME}'!")
                db_client.update_time_to_live(
                    TableName=settings.db.USERS_TABLE_NAME,
                    TimeToLiveSpecification={"Enabled": True, "AttributeName": "ttl"},
                    )
            else:
                raise RuntimeError(f"Production table {settings.db.USERS_TABLE_NAME} does not exist! Deploy it via CI/CD first.")
        else:
            raise e