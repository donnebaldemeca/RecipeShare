from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from scripts.create_table import create_table
from scripts.create_db_connection import create_db_connection

# 1. Handle startup/shutdown cleanly
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Store settings inside app.state on boot
    app.state.settings = settings

    # 2. Initialize dynamo db connection, and create table
    db_client, db_resource = create_db_connection(app.state.settings)
    
    create_table(db_client, app.state.settings)

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