from dataclasses import asdict
from typing import Any, cast

from backend.adapters.implementations.GameAdapterSQL_V2 import GameAdapterSQL_V2
from backend.adapters.interfaces.GameAdapter import GameAdapter
from backend.engine.GameEngineService import GameEngineService
from backend.engine.Movement import Movement
from backend.models.GameModels import GameCreateRequest, MovementRequest
from backend.services.interfaces.GameService import GameService


class GameServiceImpl(GameService):
    def __init__(self, game_adapter: GameAdapter | None = None):
        self.game_adapter = game_adapter or GameAdapterSQL_V2()
        self.active_games: dict[int, dict[str, Any]] = {}

    # Convierte el estado del motor en JSON guardable.
    def _engine_state(self, engine_service: GameEngineService) -> dict:
        return engine_service.get_state()

    # Obtiene o reconstruye el motor de una partida activa.
    def _get_engine_service(self, game_id: int) -> GameEngineService | None:
        game = self.active_games.get(game_id)
        if game is not None:
            return cast(GameEngineService, game["engine_service"])

        saved_game = self.game_adapter.find_by_id(game_id)
        if saved_game is None:
            return None

        board_state = saved_game.get("board_state")
        if not board_state:
            return None

        engine_service = GameEngineService()
        engine_service.load_state(board_state)
        self.active_games[game_id] = {
            "id": game_id,
            "engine_service": engine_service,
        }
        return engine_service

    # Crea una partida y arranca el motor de ajedrez.
    def create_game(self, request: GameCreateRequest) -> dict:
        engine_service = GameEngineService()
        engine_service.start_game()
        board_state = self._engine_state(engine_service)

        saved_game = self.game_adapter.save_game(
            request.white_user_id,
            request.black_user_id,
            board_state,
        )

        self.active_games[saved_game["id"]] = {
            "id": saved_game["id"],
            "engine_service": engine_service,
        }

        return saved_game

    # Lista partidas guardadas activas.
    def list_games(self) -> list[dict]:
        return self.game_adapter.find_all()

    # Busca una partida por id.
    def get_game(self, game_id: int) -> dict | None:
        return self.game_adapter.find_by_id(game_id)

    # Devuelve el tablero actual de la partida.
    def get_board(self, game_id: int) -> list[dict] | None:
        if self.game_adapter.find_by_id(game_id) is None:
            return None

        engine_service = self._get_engine_service(game_id)
        if engine_service is None:
            return None

        board = engine_service.get_board()
        return [asdict(piece) for piece in board]

    # Devuelve partida, tablero y turno actual.
    def get_state(self, game_id: int) -> dict | None:
        saved_game = self.game_adapter.find_by_id(game_id)
        if saved_game is None:
            return None

        engine_service = self._get_engine_service(game_id)
        board = self.get_board(game_id)
        board_state = engine_service.get_state() if engine_service is not None else saved_game.get("board_state")

        return {
            "game": {
                "id": saved_game["id"],
                "white_user_id": saved_game["white_user_id"],
                "black_user_id": saved_game["black_user_id"],
                "active": saved_game["active"],
                "updated_at": saved_game.get("updated_at"),
            },
            "board": board if board is not None else (board_state or {}).get("board", []),
            "turn": (board_state or {}).get("turn", "BLANCA"),
        }

    # Realiza un movimiento usando el motor de ajedrez.
    def make_move(self, game_id: int, request: MovementRequest) -> dict | None:
        if self.game_adapter.find_by_id(game_id) is None:
            return None

        engine_service = self._get_engine_service(game_id)
        if engine_service is None:
            return None

        movement = Movement(
            from_x=request.from_x,
            from_y=request.from_y,
            to_x=request.to_x,
            to_y=request.to_y,
        )
        moved = engine_service.make_move(movement)
        if not moved:
            raise ValueError("Movimiento invalido")

        self.game_adapter.update_board_state(game_id, self._engine_state(engine_service))

        return {
            "moved": True,
            "board": self.get_board(game_id),
            "turn": engine_service.game.turn.value,
        }

    # Borra la partida en base de datos y limpia su motor en memoria.
    def delete_game(self, game_id: int) -> bool:
        self.active_games.pop(game_id, None)
        return self.game_adapter.delete_game(game_id)
