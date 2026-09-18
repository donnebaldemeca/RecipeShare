import boto3
from botocore.exceptions import ClientError
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

# 1. Handle startup/shutdown cleanly
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Store settings inside app.state on boot
    app.state.settings = settings

    # 2. Initialize the Boto3
    if app.state.settings.aws.DYNAMODB_ENDPOINT:
        db_client = boto3.client(
            'dynamodb', 
            region_name=app.state.settings.aws.REGION,          # Dummy region required by boto3
            aws_access_key_id=app.state.settings.aws.ACCESS_KEY_ID,        # Dummy credentials required locally
            aws_secret_access_key=app.state.settings.aws.SECRET_ACCESS_KEY,
            endpoint_url=app.state.settings.aws.DYNAMODB_ENDPOINT
        )
        db_resource = boto3.resource(
            'dynamodb', 
            region_name=app.state.settings.aws.REGION,          # Dummy region required by boto3
            aws_access_key_id=app.state.settings.aws.ACCESS_KEY_ID,        # Dummy credentials required locally
            aws_secret_access_key=app.state.settings.aws.SECRET_ACCESS_KEY,
            endpoint_url=app.state.settings.aws.DYNAMODB_ENDPOINT
        )
    else:
        db_client = boto3.client('dynamodb', region_name=app.state.settings.aws.REGION)
        db_resource = boto3.resource('dynamodb', region_name=app.state.settings.aws.REGION)
        
    # 2. Check if table exists, create if missing
    try:
        db_client.describe_table(TableName=app.state.settings.db.USERS_TABLE_NAME)
        print(f"Table '{settings.db.USERS_TABLE_NAME}' already exists locally.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"Table '{settings.db.USERS_TABLE_NAME}' not found locally. Creating it now...")
            
            db_client.create_table(
                TableName=settings.db.USERS_TABLE_NAME,
                AttributeDefinitions=[
                    {'AttributeName': 'UserId', 'AttributeType': 'S'}
                ],
                KeySchema=[
                    {'AttributeName': 'UserId', 'KeyType': 'HASH'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Local DynamoDB is instant, but keeping the waiter is a safe best practice
            waiter = db_client.get_waiter('table_exists')
            waiter.wait(TableName=settings.db.USERS_TABLE_NAME)
            print(f"Local table '{settings.db.USERS_TABLE_NAME}' is now active!")
        else:
            raise e

    # 3. Save the resource to app.state for your endpoints to use
    app.state.db = db_resource
    yield
    # Clean up operations go here on shutdown (if any)

# 2. Ultra-lean Application Factory
def create_app() -> FastAPI:
    app = FastAPI(
        title="RecipeShare", 
        lifespan=lifespan
    )

    # Modular Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # # Single-line route registration
    # app.include_router(api_router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)