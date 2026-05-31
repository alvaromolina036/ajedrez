from backend.adapters.implementations.UserAdapterSQL_V2 import UserAdapterSQL_V2
from backend.adapters.interfaces.UserAdapter import UserAdapter
from backend.services.interfaces.AuthenticationService import AuthenticationService
from backend.utils.SecurityUtils import create_jwt, verify_jwt, verify_password


class AuthenticationServiceImpl(AuthenticationService):
    def __init__(self, user_adapter: UserAdapter | None = None):
        self.user_adapter = user_adapter or UserAdapterSQL_V2()

    # Comprueba credenciales reales y genera un JWT.
    def login(self, username: str, password: str) -> str:
        user = self.user_adapter.find_credentials_by_username(username)
        if user is None:
            raise ValueError("Credenciales invalidas")

        if not verify_password(password, user["password_hash"]):
            raise ValueError("Credenciales invalidas")

        return create_jwt({
            "user_id": user["id"],
            "username": user["username"],
        })

    # Valida firma y caducidad de un JWT.
    def validate_token(self, token: str) -> bool:
        return verify_jwt(token) is not None
