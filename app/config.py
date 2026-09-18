from typing import Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. Create simple sub-models for grouped categories
class AWSSettings(BaseModel):
    REGION: str = "us-east-1"
    DYNAMODB_ENDPOINT: Optional[str] = None  # Populated via DYNAMODB_ENDPOINT locally
    ACCESS_KEY_ID: str = "localdev"
    SECRET_ACCESS_KEY: str = "localdev"

class DatabaseSettings(BaseModel):
    USERS_TABLE_NAME: str = "Local_Users_Table"

# 2. Embed them into the main global Settings class
class Settings(BaseSettings):
    # App core settings
    ENV: str = "development"
    DEBUG: bool = True
    
    # Nested configurations
    aws: AWSSettings = AWSSettings()
    db: DatabaseSettings = DatabaseSettings()

    # Tells Pydantic how to handle .env parsing
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # This allows you to map flat .env variables to nested objects
        # e.g., AWS_REGION sets settings.aws.REGION automatically
        env_nested_delimiter="__", 
        extra="ignore"
    )

settings = Settings()