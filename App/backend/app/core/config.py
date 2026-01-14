from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Trippy"

    # Database
    DATABASE_URL: str = "postgresql://localhost:5432/trippy"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
