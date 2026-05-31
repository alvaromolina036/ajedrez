import json

from backend.adapters.implementations.DatabaseConnection import get_connection
from backend.adapters.interfaces.GameAdapter import GameAdapter


class GameAdapterSQL_V1(GameAdapter):

    # Convierte JSON de MariaDB a diccionario Python.
    def _decode_board_state(self, board_state):
        if board_state is None or isinstance(board_state, dict):
            return board_state
        return json.loads(board_state)

    # Busca una partida por id usando SQL parametrizado.
    def find_by_id(self, game_id: int) -> dict | None:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, white_user_id, black_user_id, active, board_state, updated_at
            FROM games
            WHERE id = %s
            """,
            (game_id,),
        )
        game = cursor.fetchone()
        cursor.close()
        connection.close()
        if game is not None:
            game["board_state"] = self._decode_board_state(game.get("board_state"))
        return game

    # Lista partidas activas usando SQL parametrizado.
    def find_live_games(self) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, white_user_id, black_user_id, active, board_state, updated_at
            FROM games
            WHERE active = %s
            ORDER BY updated_at DESC
            """,
            (True,),
        )
        games = cursor.fetchall()
        cursor.close()
        connection.close()
        for game in games:
            game["board_state"] = self._decode_board_state(game.get("board_state"))
        return games

    # Guarda una partida usando SQL parametrizado.
    def save_game(self, white_user_id: int, black_user_id: int, board_state: dict | None = None) -> dict:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO games (white_user_id, black_user_id, active, board_state)
            VALUES (%s, %s, %s, %s)
            """,
            (white_user_id, black_user_id, True, json.dumps(board_state) if board_state is not None else None),
        )
        connection.commit()
        game_id = cursor.lastrowid
        cursor.close()
        connection.close()
        return {
            "id": game_id,
            "white_user_id": white_user_id,
            "black_user_id": black_user_id,
            "active": True,
            "board_state": board_state,
            "updated_at": None,
        }

    # Guarda el estado completo del tablero usando SQL parametrizado.
    def update_board_state(self, game_id: int, board_state: dict) -> dict | None:
        if self.find_by_id(game_id) is None:
            return None

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE games SET board_state = %s WHERE id = %s",
            (json.dumps(board_state), game_id),
        )
        connection.commit()
        cursor.close()
        connection.close()
        return self.find_by_id(game_id)

    # Actualiza si una partida sigue activa usando SQL parametrizado.
    def update_active_state(self, game_id: int, active: bool) -> dict | None:
        if self.find_by_id(game_id) is None:
            return None

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE games SET active = %s WHERE id = %s",
            (active, game_id),
        )
        connection.commit()
        cursor.close()
        connection.close()
        return self.find_by_id(game_id)

    # Borra una partida usando SQL parametrizado.
    def delete_game(self, game_id: int) -> bool:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM games WHERE id = %s",
            (game_id,),
        )
        connection.commit()
        deleted = cursor.rowcount > 0
        cursor.close()
        connection.close()
        return deleted
