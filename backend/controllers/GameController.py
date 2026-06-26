from fastapi import APIRouter, Depends, HTTPException
from backend.models.GameModels import GameCreateRequest, MovementRequest
from backend.services.implementations.GameServiceImpl import GameServiceImpl
from backend.utils.AuthDependencies import require_authenticated_user

router = APIRouter(prefix="/games", tags=["games"])
game_service = GameServiceImpl()


def validate_game_id(game_id: int):
    if game_id <= 0:
        raise HTTPException(status_code=400, detail="El game_id debe ser mayor que 0")


def validate_board_coordinate(value: int, field_name: str):
    if value < 0 or value > 7:
        raise HTTPException(
            status_code=400,
            detail=f"La coordenada {field_name} debe estar entre 0 y 7",
        )


# Lista partidas guardadas activas.
@router.get("")
def list_games(authenticated_user: dict = Depends(require_authenticated_user)):
    return game_service.list_games()


# Crea una partida nueva entre dos usuarios.
@router.post("")
def create_game(request: GameCreateRequest, authenticated_user: dict = Depends(require_authenticated_user)):
    if request.white_user_id <= 0:
        raise HTTPException(status_code=400, detail="white_user_id debe ser mayor que 0")
    if request.black_user_id <= 0:
        raise HTTPException(status_code=400, detail="black_user_id debe ser mayor que 0")
    if request.white_user_id == request.black_user_id:
        raise HTTPException(status_code=400, detail="Los jugadores deben ser distintos")

    try:
        game = game_service.create_game(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return game


# Obtiene la informacion general de una partida.
@router.get("/{game_id}")
def get_game(game_id: int, authenticated_user: dict = Depends(require_authenticated_user)):
    validate_game_id(game_id)

    game = game_service.get_game(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    return game


# Obtiene el tablero actual de una partida.
@router.get("/{game_id}/board")
def get_board(game_id: int, authenticated_user: dict = Depends(require_authenticated_user)):
    validate_game_id(game_id)

    board = game_service.get_board(game_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    return board


# Obtiene estado completo de una partida.
@router.get("/{game_id}/state")
def get_state(game_id: int, authenticated_user: dict = Depends(require_authenticated_user)):
    validate_game_id(game_id)

    state = game_service.get_state(game_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    return state


# Recibe un movimiento y lo envia al servicio de partidas.
@router.put("/{game_id}/move")
def make_move(
    game_id: int,
    request: MovementRequest,
    authenticated_user: dict = Depends(require_authenticated_user),
):
    validate_game_id(game_id)
    validate_board_coordinate(request.from_x, "from_x")
    validate_board_coordinate(request.from_y, "from_y")
    validate_board_coordinate(request.to_x, "to_x")
    validate_board_coordinate(request.to_y, "to_y")

    try:
        result = game_service.make_move(game_id, request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if result is None:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    return result


# Elimina o finaliza una partida existente.
@router.delete("/{game_id}")
def delete_game(game_id: int, authenticated_user: dict = Depends(require_authenticated_user)):
    validate_game_id(game_id)

    deleted = game_service.delete_game(game_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    return {"message": "Partida borrada correctamente"}
