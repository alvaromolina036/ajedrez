from pydantic import BaseModel


# Datos que recibe el login.
class LoginRequest(BaseModel):
    username: str
    password: str
