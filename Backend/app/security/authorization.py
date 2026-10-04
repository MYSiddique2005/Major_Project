"""Permission checks used as FastAPI dependencies. This is the real security boundary."""
from fastapi import Depends, HTTPException, status

from app.models.entities import User
from app.security.authentication import get_current_user
from app.security.permissions import Permission, has_permission


def require_permission(permission: Permission):
    """Dependency factory: resolves the current user and rejects them with 403 if they lack `permission`."""

    def dependency(user: User = Depends(get_current_user)) -> User:
        if not has_permission(user.role, permission):
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Your role does not have the '{permission}' permission")
        return user

    return dependency
