import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Handle startup/shutdown cleanly
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and variables
    env = os.getenv("APP_ENV", "local")
    app.state.env = env
    app.state.db = DatabaseFactory.get_database()
    
    yield  
    
    # Shutdown: Clean up connections here if needed (e.g., db.close())
    pass
# 2. Ultra-lean Application Factory
def create_app() -> FastAPI:
    app = FastAPI(
        title="AWS Fargate FastAPI Modular Service", 
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

    # Single-line route registration
    app.include_router(api_router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)