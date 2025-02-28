"""Authentication module for the application."""

# This file intentionally left empty to mark the directory as a Python package

# Import only what's needed by other modules
from app.auth.jwt import authenticate_user, get_password_hash, verify_password
