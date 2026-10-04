from functools import lru_cache

from app.core.security import hash_password
from app.mock_data.users import USERS
from app.models.entities import User
from app.repositories.base import InMemoryRepository, UserRepository


@lru_cache
def _seed() -> tuple[dict, ...]:
    """Hash the demo passwords once per process (bcrypt is deliberately slow)."""
    return tuple(
        {**{k: v for k, v in user.items() if k != "password"}, "hashed_password": hash_password(user["password"])}
        for user in USERS
    )


class MockUserRepository(InMemoryRepository[User], UserRepository):
    def __init__(self):
        super().__init__(User, list(_seed()), id_prefix="U", id_width=3)

    def get_by_username(self, username: str) -> User | None:
        for user in self.list():
            if user.username == username:
                return user
        return None
