from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    APP_NAME: str = "Trippy"

    # Database (Postgres preferred; sqlite:///./trippy.db works for local smoke tests)
    DATABASE_URL: str = "postgresql+psycopg://trippy:trippy@localhost:5432/trippy"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Auth
    SECRET_KEY: str = "dev-secret-change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"


settings = Settings()
