from abc import ABC, abstractmethod

from backend.models.GameModels import GameCreateRequest, MovementRequest


class GameService(ABC):

    # Crea una partida nueva.
    @abstractmethod
    def create_game(self, request: GameCreateRequest) -> dict:
        pass

    # Lista partidas guardadas activas.
    @abstractmethod
    def list_games(self) -> list[dict]:
        pass

    # Busca una partida por id.
    @abstractmethod
    def get_game(self, game_id: int) -> dict | None:
        pass

    # Devuelve el tablero de una partida.
    @abstractmethod
    def get_board(self, game_id: int) -> list[dict] | None:
        pass

    # Devuelve partida, tablero y turno en una sola respuesta.
    @abstractmethod
    def get_state(self, game_id: int) -> dict | None:
        pass

    # Realiza un movimiento en una partida.
    @abstractmethod
    def make_move(self, game_id: int, request: MovementRequest) -> dict | None:
        pass

    # Borra o finaliza una partida.
    @abstractmethod
    def delete_game(self, game_id: int) -> bool:
        pass
