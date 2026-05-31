from fastapi import APIRouter, Depends, HTTPException, Query
from backend.models.UserModels import UserCreateRequest, UserUpdateRequest
from backend.services.implementations.UserServiceImpl import UserServiceImpl
from backend.utils.AuthDependencies import require_authenticated_user
from backend.utils.WebSocketManager import websocket_manager

router = APIRouter(prefix="/users", tags=["users"])
user_service = UserServiceImpl()


# Busca usuarios por id exacto o username parcial.
@router.get("/search")
def search_users(
    query: str = Query(...),
    authenticated_user: dict = Depends(require_authenticated_user),
):
    if not query.strip():
        raise HTTPException(status_code=400, detail="El query no puede estar vacio")

    return user_service.search_users(query.strip())


# Devuelve usuarios conectados por WebSocket.
@router.get("/online")
def get_online_users(authenticated_user: dict = Depends(require_authenticated_user)):
    return websocket_manager.online_users()


# Busca un usuario usando su id en el path.
@router.get("/{user_id}")
def get_user_by_id(user_id: int, authenticated_user: dict = Depends(require_authenticated_user)):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="El user_id debe ser mayor que 0")

    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# Busca un usuario usando username como query parameter.
@router.get("")
def get_user_by_username(
    username: str = Query(...),
    authenticated_user: dict = Depends(require_authenticated_user),
):
    if not username.strip():
        raise HTTPException(status_code=400, detail="El username no puede estar vacio")

    user = user_service.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# Crea un nuevo usuario con los datos del body.
@router.post("")
def create_user(request: UserCreateRequest):
    if not request.username.strip():
        raise HTTPException(status_code=400, detail="El username es obligatorio")
    if not request.password.strip():
        raise HTTPException(status_code=400, detail="La password es obligatoria")

    try:
        return user_service.create_user(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# Actualiza los datos de un usuario existente.
@router.put("/{user_id}")
def update_user(
    user_id: int,
    request: UserUpdateRequest,
    authenticated_user: dict = Depends(require_authenticated_user),
):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="El user_id debe ser mayor que 0")
    if request.username is None and request.password is None:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")
    if request.username is not None and not request.username.strip():
        raise HTTPException(status_code=400, detail="El username no puede estar vacio")
    if request.password is not None and not request.password.strip():
        raise HTTPException(status_code=400, detail="La password no puede estar vacia")

    user = user_service.update_user(user_id, request)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# Borra un usuario usando su id en el path.
@router.delete("/{user_id}")
def delete_user(user_id: int, authenticated_user: dict = Depends(require_authenticated_user)):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="El user_id debe ser mayor que 0")

    deleted = user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario borrado correctamente"}
