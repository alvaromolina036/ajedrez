from backend.adapters.implementations.UserAdapterSQL_V2 import UserAdapterSQL_V2
from backend.adapters.interfaces.UserAdapter import UserAdapter
from backend.models.UserModels import UserCreateRequest, UserUpdateRequest
from backend.services.interfaces.UserService import UserService
from backend.utils.SecurityUtils import hash_password


class UserServiceImpl(UserService):
    def __init__(self, user_adapter: UserAdapter | None = None):
        self.user_adapter = user_adapter or UserAdapterSQL_V2()

    # Busca un usuario por id usando el adapter.
    def get_user_by_id(self, user_id: int) -> dict | None:
        return self.user_adapter.find_by_id(user_id)

    # Busca un usuario por username usando el adapter.
    def get_user_by_username(self, username: str) -> dict | None:
        return self.user_adapter.find_by_username(username)

    # Busca usuarios por id exacto o username parcial.
    def search_users(self, query: str) -> list[dict]:
        return self.user_adapter.search_users(query)

    # Crea un usuario usando el adapter.
    def create_user(self, request: UserCreateRequest) -> dict:
        if self.get_user_by_username(request.username) is not None:
            raise ValueError("Ya existe un usuario con ese username")

        hashed_request = UserCreateRequest(
            username=request.username,
            password=hash_password(request.password),
        )
        return self.user_adapter.save_user(hashed_request)

    # Actualiza un usuario usando el adapter.
    def update_user(self, user_id: int, request: UserUpdateRequest) -> dict | None:
        password = hash_password(request.password) if request.password is not None else None
        hashed_request = UserUpdateRequest(
            username=request.username,
            password=password,
        )
        return self.user_adapter.update_user(user_id, hashed_request)

    # Borra un usuario usando el adapter.
    def delete_user(self, user_id: int) -> bool:
        return self.user_adapter.delete_user(user_id)
