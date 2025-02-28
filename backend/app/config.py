"""
Configuration module for the WorkflowForge application.

This module handles loading configuration from environment variables,
configuration files, and provides defaults for development environments.
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=str(env_path))

# Determine the environment
ENV = os.getenv("ENVIRONMENT", "development").lower()


class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    url: str = Field(default="workflows.db")
    echo: bool = Field(default=False)
    connect_args: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "allow"}


class APIConfig(BaseModel):
    """API server configuration settings."""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)
    debug: bool = Field(default=True)
    workers: int = Field(default=1)

    model_config = {"extra": "allow"}


class CORSConfig(BaseModel):
    """CORS configuration settings."""
    allowed_origins: List[str] = Field(default=["*"])
    allow_credentials: bool = Field(default=True)
    allow_methods: List[str] = Field(default=["*"])
    allow_headers: List[str] = Field(default=["*"])
    max_age: int = Field(default=600)  # 10 minutes in seconds

    model_config = {"extra": "allow"}


class RateLimitConfig(BaseModel):
    """Rate limiting configuration settings."""
    enabled: bool = Field(default=False)
    per_minute: int = Field(default=60)  # Requests per minute
    window_size: int = Field(default=60)  # Window size in seconds

    model_config = {"extra": "allow"}


class WorkflowConfig(BaseModel):
    """Workflow execution configuration settings."""
    use_mock: bool = Field(default=True)
    timeout_seconds: float = Field(default=30.0)
    max_retries: int = Field(default=3)

    model_config = {"extra": "allow"}


class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    level: str = Field(default="INFO")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file: Optional[str] = Field(default=None)

    model_config = {"extra": "allow"}


class AppConfig(BaseModel):
    """Main application configuration."""
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    secret_key: str = Field(default="supersecretkey")  # Change in production!

    model_config = {"extra": "allow"}


# Load config based on environment
def load_config() -> AppConfig:
    """Load configuration based on the current environment."""
    # Base configuration
    config = AppConfig(environment=ENV)

    # Create updated configs with environment variable values
    db_updates = {}
    api_updates = {}
    cors_updates = {}
    rate_limit_updates = {}
    workflow_updates = {}
    logging_updates = {}
    app_updates = {}

    # Override with environment variables
    if os.getenv("DATABASE_URL"):
        db_updates["url"] = os.getenv("DATABASE_URL")

    if os.getenv("API_HOST"):
        api_updates["host"] = os.getenv("API_HOST")

    if os.getenv("API_PORT"):
        api_updates["port"] = int(os.getenv("API_PORT"))

    if os.getenv("API_RELOAD"):
        api_updates["reload"] = os.getenv("API_RELOAD").lower() == "true"

    if os.getenv("API_DEBUG"):
        api_updates["debug"] = os.getenv("API_DEBUG").lower() == "true"

    # CORS configuration
    if os.getenv("CORS_ALLOWED_ORIGINS"):
        cors_updates["allowed_origins"] = os.getenv(
            "CORS_ALLOWED_ORIGINS").split(",")

    # Rate limiting configuration
    if os.getenv("RATE_LIMIT_ENABLED"):
        rate_limit_updates["enabled"] = os.getenv(
            "RATE_LIMIT_ENABLED").lower() == "true"

    if os.getenv("RATE_LIMIT_PER_MINUTE"):
        rate_limit_updates["per_minute"] = int(
            os.getenv("RATE_LIMIT_PER_MINUTE"))

    if os.getenv("USE_MOCK_WORKFLOW"):
        workflow_updates["use_mock"] = os.getenv(
            "USE_MOCK_WORKFLOW").lower() == "true"

    if os.getenv("LOG_LEVEL"):
        logging_updates["level"] = os.getenv("LOG_LEVEL")

    if os.getenv("LOG_FILE"):
        logging_updates["file"] = os.getenv("LOG_FILE")

    if os.getenv("SECRET_KEY"):
        app_updates["secret_key"] = os.getenv("SECRET_KEY")

    # Apply updates using model_copy
    if db_updates:
        config.database = config.database.model_copy(update=db_updates)

    if api_updates:
        config.api = config.api.model_copy(update=api_updates)

    if cors_updates:
        config.cors = config.cors.model_copy(update=cors_updates)

    if rate_limit_updates:
        config.rate_limit = config.rate_limit.model_copy(
            update=rate_limit_updates)

    if workflow_updates:
        config.workflow = config.workflow.model_copy(update=workflow_updates)

    if logging_updates:
        config.logging = config.logging.model_copy(update=logging_updates)

    # Production-specific overrides
    if ENV == "production":
        app_updates["debug"] = False
        api_updates["debug"] = False
        api_updates["reload"] = False

        # Production CORS settings if not explicitly set
        if not os.getenv("CORS_ALLOWED_ORIGINS"):
            cors_updates["allowed_origins"] = [
                "https://workflowforge.com",
                "https://app.workflowforge.com",
                "https://api.workflowforge.com"
            ]
            cors_updates["allow_methods"] = [
                "GET", "POST", "PUT", "DELETE", "OPTIONS"]
            cors_updates["allow_headers"] = ["Authorization", "Content-Type"]
            cors_updates["max_age"] = 86400  # 24 hours in seconds

        # Enable rate limiting in production by default
        if not os.getenv("RATE_LIMIT_ENABLED"):
            rate_limit_updates["enabled"] = True

        # Apply production updates
        config = config.model_copy(update=app_updates)
        config.api = config.api.model_copy(update=api_updates)
        config.cors = config.cors.model_copy(update=cors_updates)
        config.rate_limit = config.rate_limit.model_copy(
            update=rate_limit_updates)

        if not os.getenv("SECRET_KEY"):
            raise ValueError(
                "SECRET_KEY must be set in production environment")

    return config


# Create global config instance
config = load_config()
