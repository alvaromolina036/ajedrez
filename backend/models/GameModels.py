from pydantic import BaseModel


# Datos necesarios para crear una partida.
class GameCreateRequest(BaseModel):
    white_user_id: int
    black_user_id: int


# Coordenadas de origen y destino de un movimiento.
class MovementRequest(BaseModel):
    from_x: int
    from_y: int
    to_x: int
    to_y: int
