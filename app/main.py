import boto3
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

# 1. Handle startup/shutdown cleanly
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Store settings inside app.state on boot
    app.state.settings = settings
    
    # 2. Initialize the Boto3 resource dynamically
    db_kwargs = {"region_name": settings.aws.AWS_REGION}
    if settings.aws.DYNAMODB_ENDPOINT:
        db_kwargs["endpoint_url"] = settings.aws.DYNAMODB_ENDPOINT
        db_kwargs["aws_access_key_id"] = settings.aws.AWS_ACCESS_KEY_ID
        db_kwargs["aws_secret_access_key"] = settings.aws.AWS_SECRET_ACCESS_KEY
        
    # 3. Store the database client connection inside app.state
    app.state.db = boto3.resource("dynamodb", **db_kwargs)
    
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