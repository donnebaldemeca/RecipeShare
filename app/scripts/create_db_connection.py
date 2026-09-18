import boto3
from pydantic_settings import BaseSettings

def create_db_connection(settings: BaseSettings):
    if settings.ENV == 'development':
        db_client = boto3.client(
            'dynamodb', 
            region_name=settings.aws.REGION,
            aws_access_key_id=settings.aws.ACCESS_KEY_ID,
            aws_secret_access_key=settings.aws.SECRET_ACCESS_KEY,
            endpoint_url=settings.aws.DYNAMODB_ENDPOINT
        )
        db_resource = boto3.resource(
            'dynamodb', 
            region_name=settings.aws.REGION,
            aws_access_key_id=settings.aws.ACCESS_KEY_ID,
            aws_secret_access_key=settings.aws.SECRET_ACCESS_KEY,
            endpoint_url=settings.aws.DYNAMODB_ENDPOINT
        )
    else:
        db_client = boto3.client('dynamodb', region_name=settings.aws.REGION)
        db_resource = boto3.resource('dynamodb', region_name=settings.aws.REGION)

    return db_client, db_resource
