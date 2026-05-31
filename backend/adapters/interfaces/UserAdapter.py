from abc import ABC, abstractmethod

from backend.models.UserModels import UserCreateRequest, UserUpdateRequest


class UserAdapter(ABC):

    # Busca un usuario por id en el almacenamiento.
    @abstractmethod
    def find_by_id(self, user_id: int) -> dict | None:
        pass

    # Busca un usuario por username en el almacenamiento.
    @abstractmethod
    def find_by_username(self, username: str) -> dict | None:
        pass

    # Busca usuarios por id exacto o username parcial.
    @abstractmethod
    def search_users(self, query: str) -> list[dict]:
        pass

    # Busca credenciales internas de un usuario para autenticar.
    @abstractmethod
    def find_credentials_by_username(self, username: str) -> dict | None:
        pass

    # Guarda un usuario nuevo.
    @abstractmethod
    def save_user(self, request: UserCreateRequest) -> dict:
        pass

    # Actualiza un usuario existente.
    @abstractmethod
    def update_user(self, user_id: int, request: UserUpdateRequest) -> dict | None:
        pass

    # Borra un usuario existente.
    @abstractmethod
    def delete_user(self, user_id: int) -> bool:
        pass
