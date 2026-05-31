from abc import ABC, abstractmethod


class AuthenticationService(ABC):

    # Inicia sesion y devuelve un token.
    @abstractmethod
    def login(self, username: str, password: str) -> str:
        pass

    # Comprueba si un token es valido.
    @abstractmethod
    def validate_token(self, token: str) -> bool:
        pass
