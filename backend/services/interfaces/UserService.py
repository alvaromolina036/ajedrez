from abc import ABC, abstractmethod

from backend.models.UserModels import UserCreateRequest, UserUpdateRequest


class UserService(ABC):

    # Busca un usuario por id.
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> dict | None:
        pass

    # Busca un usuario por username.
    @abstractmethod
    def get_user_by_username(self, username: str) -> dict | None:
        pass

    # Busca usuarios por id o username parcial.
    @abstractmethod
    def search_users(self, query: str) -> list[dict]:
        pass

    # Crea un usuario nuevo.
    @abstractmethod
    def create_user(self, request: UserCreateRequest) -> dict:
        pass

    # Actualiza un usuario existente.
    @abstractmethod
    def update_user(self, user_id: int, request: UserUpdateRequest) -> dict | None:
        pass

    # Borra un usuario existente.
    @abstractmethod
    def delete_user(self, user_id: int) -> bool:
        pass
