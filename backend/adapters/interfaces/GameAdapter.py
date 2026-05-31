from abc import ABC, abstractmethod


class GameAdapter(ABC):

    # Busca una partida por id.
    @abstractmethod
    def find_by_id(self, game_id: int) -> dict | None:
        pass

    # Lista partidas activas.
    @abstractmethod
    def find_live_games(self) -> list[dict]:
        pass

    # Guarda una partida nueva.
    @abstractmethod
    def save_game(self, white_user_id: int, black_user_id: int, board_state: dict | None = None) -> dict:
        pass

    # Guarda el estado completo del tablero.
    @abstractmethod
    def update_board_state(self, game_id: int, board_state: dict) -> dict | None:
        pass

    # Actualiza el estado activo de una partida.
    @abstractmethod
    def update_active_state(self, game_id: int, active: bool) -> dict | None:
        pass

    # Borra una partida existente.
    @abstractmethod
    def delete_game(self, game_id: int) -> bool:
        pass
