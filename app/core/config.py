from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "SpendWise AI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    HOST: str = "127.0.0.1"
    PORT: int = 5000

    # Supabase Configuration
    SUPABASE_URL: str = Field(default="", description="Supabase project URL")
    SUPABASE_KEY: str = Field(default="", description="Supabase Anon or Service Role Key")
    SUPABASE_JWT_SECRET: str = Field(default="", description="Supabase JWT secret for token verification")

    # Optional AI Keys (Gemini / OpenAI for enhanced contextual chat)
    GEMINI_API_KEY: Optional[str] = Field(default=None, description="Optional Google Gemini API key")
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="Optional OpenAI API key")

    # CORS configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
