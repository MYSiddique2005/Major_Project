from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.models.entities import User
from app.models.enums import AuditAction, AuditStatus
from app.repositories.base import UnitOfWork, UserRepository
from app.schemas.auth import TokenResponse, UserResponse
from app.security.permissions import permissions_for
from app.services.audit_service import AuditService


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, users: UserRepository, audit: AuditService, uow: UnitOfWork):
        self._uow = uow
        self._users = users
        self._audit = audit

    @staticmethod
    def to_response(user: User) -> UserResponse:
        return UserResponse(
            id=user.id, username=user.username, full_name=user.full_name, email=user.email,
            role=user.role, permissions=permissions_for(user.role),
        )

    def login(self, username: str, password: str) -> TokenResponse:
        user = self._users.get_by_username(username)
        if user is None or not user.is_active or not verify_password(password, user.hashed_password):
            self._audit.record(
                action=AuditAction.LOGIN, entity="User", entity_id=user.id if user else "unknown",
                description="Invalid username or password", username=username[:64], status=AuditStatus.FAILED,
            )
            self._uow.commit()  # keep the failed attempt even though the request errors
            raise InvalidCredentialsError
        self._audit.record(
            action=AuditAction.LOGIN, entity="User", entity_id=user.id, description="User logged in", user=user
        )
        self._uow.commit()
        return TokenResponse(
            access_token=create_access_token(user.username, user.role),
            expires_in=get_settings().access_token_expire_minutes * 60,
            user=self.to_response(user),
        )
