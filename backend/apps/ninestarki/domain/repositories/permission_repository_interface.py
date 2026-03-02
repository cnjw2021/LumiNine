from abc import ABC, abstractmethod
from typing import List
from apps.ninestarki.domain.entities.permission import Permission

class IPermissionRepository(ABC):
    @abstractmethod
    def find_by_name(self, name: str) -> Permission | None:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Permission]:
        pass

    @abstractmethod
    def save(self, permission: Permission) -> Permission:
        pass