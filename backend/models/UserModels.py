from pydantic import BaseModel


# Datos necesarios para crear un usuario.
class UserCreateRequest(BaseModel):
    username: str
    password: str


# Datos opcionales para actualizar un usuario.
class UserUpdateRequest(BaseModel):
    username: str | None = None
    password: str | None = None
