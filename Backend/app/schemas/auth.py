from pydantic import BaseModel, Field

from app.models.enums import Role


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, examples=["admin"])
    password: str = Field(min_length=1, examples=["admin123"])


class UserResponse(BaseModel):
    id: str
    username: str
    full_name: str
    email: str
    role: Role
    permissions: list[str]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token lifetime in seconds")
    user: UserResponse
