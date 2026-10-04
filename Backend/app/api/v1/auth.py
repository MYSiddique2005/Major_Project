from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_auth_service
from app.models.entities import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.security.authentication import get_current_user
from app.services.auth_service import AuthService, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="Log in and receive a JWT access token")
def login(credentials: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    try:
        return service.login(credentials.username, credentials.password)
    except InvalidCredentialsError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password") from None


@router.get("/me", response_model=UserResponse, summary="Current user profile, role and permissions")
def me(user: User = Depends(get_current_user)) -> UserResponse:
    return AuthService.to_response(user)
