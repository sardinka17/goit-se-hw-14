from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: str
    mail_server: str
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'


settings = Settings()
