from fastapi import APIRouter, Header, HTTPException
from backend.models.AuthenticationModels import LoginRequest
from backend.services.implementations.AuthenticationServiceImpl import AuthenticationServiceImpl

router = APIRouter(prefix="/authentication", tags=["authentication"])
authentication_service = AuthenticationServiceImpl()


# Inicia sesion y devuelve un JWT.
@router.post("/login")
def login(request: LoginRequest):
    if not request.username.strip():
        raise HTTPException(status_code=400, detail="El username es obligatorio")
    if not request.password.strip():
        raise HTTPException(status_code=400, detail="La password es obligatoria")

    try:
        token = authentication_service.login(request.username, request.password)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error))

    return {
        "token": token,
    }


# Comprueba si el token enviado existe y se puede validar.
@router.get("/verify")
def verify_token(authorization: str | None = Header(default=None)):
    if authorization is None or not authorization.strip():
        raise HTTPException(status_code=401, detail="Falta el header Authorization")

    valid = authentication_service.validate_token(authorization)
    if not valid:
        raise HTTPException(status_code=401, detail="Token invalido")

    return {
        "valid": valid,
    }
