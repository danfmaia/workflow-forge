"""Authentication API endpoints for WorkflowForge."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.jwt import (
    Token, User,
    authenticate_user, create_access_token,
    get_current_active_user, fake_users_db,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get an access token for authentication.

    Args:
        form_data: The OAuth2 password request form containing username and password.

    Returns:
        A Token object containing the access token and token type.

    Raises:
        HTTPException: If authentication fails.
    """
    user = authenticate_user(
        fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get information about the currently authenticated user.

    Args:
        current_user: The current authenticated user.

    Returns:
        The User object for the current user.
    """
    return current_user


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    """
    A protected endpoint that requires authentication.

    Args:
        current_user: The current authenticated user.

    Returns:
        A message indicating successful access.
    """
    return {"message": "You have access to this protected endpoint"}
