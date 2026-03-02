from abc import ABC, abstractmethod
from typing import Optional
from apps.ninestarki.domain.entities.user import User

class IUserRepository(ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user: User, deleted_by_user: User) -> None:
        pass
