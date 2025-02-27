"""JWT authentication module for WorkflowForge."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import config

# Security constants
SECRET_KEY = config.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None


class User(BaseModel):
    """User model."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str


# Mock user database - replace with actual database in production
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrator",
        "email": "admin@workflowforge.com",
        "hashed_password": pwd_context.hash("adminpassword"),
        "disabled": False,
    },
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@workflowforge.com",
        "hashed_password": pwd_context.hash("testpassword"),
        "disabled": False,
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)


def get_user(db, username: str) -> Optional[UserInDB]:
    """Get a user from the database."""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(fake_db, username: str, password: str) -> Union[User, bool]:
    """Authenticate a user."""
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify a JWT token and return the token data."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        # Check if token is expired
        if "exp" in payload:
            expiration = datetime.fromtimestamp(payload["exp"])
            if datetime.utcnow() > expiration:
                raise expired_exception

        token_data = TokenData(username=username)
        return token_data
    except JWTError as e:
        # Check if it's an expired token error
        if "Signature has expired" in str(e):
            raise expired_exception
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from a JWT token."""
    token_data = verify_token(token)
    user = get_user(fake_users_db, token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user."""
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
