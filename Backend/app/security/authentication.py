"""Resolves the current user from the bearer token."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import get_user_repository
from app.core.security import decode_access_token
from app.models.entities import User
from app.repositories.base import UserRepository

bearer_scheme = HTTPBearer(auto_error=False, description="Paste the access_token returned by /auth/login")


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail, headers={"WWW-Authenticate": "Bearer"})


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    users: UserRepository = Depends(get_user_repository),
) -> User:
    if credentials is None:
        raise _unauthorized("Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise _unauthorized("Invalid or expired token")
    user = users.get_by_username(payload.get("sub", ""))
    if user is None or not user.is_active:
        raise _unauthorized("Invalid or expired token")
    return user
