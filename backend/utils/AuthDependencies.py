from fastapi import Header, HTTPException

from backend.utils.SecurityUtils import verify_jwt


# Valida el JWT recibido en el header Authorization.
def require_authenticated_user(authorization: str | None = Header(default=None)) -> dict:
    if authorization is None or not authorization.strip():
        raise HTTPException(status_code=401, detail="Falta el header Authorization")

    payload = verify_jwt(authorization)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token invalido")

    return payload
