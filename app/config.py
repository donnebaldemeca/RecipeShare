from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True

    AWS_REGION: str = "us-east-1"
    USERS_TABLE_NAME: str = "Local_Users_Table"
    DYNAMODB_ENDPOINT: Optional[str] = None
    
    # Static fallbacks for local docker container auth
    AWS_ACCESS_KEY_ID: str = "localdev"
    AWS_SECRET_ACCESS_KEY: str = "localdev"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()