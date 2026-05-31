from backend.adapters.implementations.ORMConnection import GameTable, SessionLocal
from backend.adapters.interfaces.GameAdapter import GameAdapter


class GameAdapterSQL_V2(GameAdapter):

    # Convierte una partida ORM en diccionario.
    def _to_dict(self, game: GameTable) -> dict:
        return {
            "id": game.id,
            "white_user_id": game.white_user_id,
            "black_user_id": game.black_user_id,
            "active": game.active,
            "board_state": game.board_state,
            "updated_at": game.updated_at.isoformat() if game.updated_at is not None else None,
        }

    # Busca una partida por id usando ORM.
    def find_by_id(self, game_id: int) -> dict | None:
        with SessionLocal() as session:
            game = session.get(GameTable, game_id)
            if game is None:
                return None
            return self._to_dict(game)

    # Lista partidas activas usando ORM.
    def find_live_games(self) -> list[dict]:
        with SessionLocal() as session:
            games = (
                session.query(GameTable)
                .filter(GameTable.active == True)
                .order_by(GameTable.updated_at.desc())
                .all()
            )
            return [self._to_dict(game) for game in games]

    # Guarda una partida usando ORM.
    def save_game(self, white_user_id: int, black_user_id: int, board_state: dict | None = None) -> dict:
        with SessionLocal() as session:
            game = GameTable(
                white_user_id=white_user_id,
                black_user_id=black_user_id,
                active=True,
                board_state=board_state,
            )
            session.add(game)
            session.commit()
            session.refresh(game)
            return self._to_dict(game)

    # Guarda el estado completo del tablero usando ORM.
    def update_board_state(self, game_id: int, board_state: dict) -> dict | None:
        with SessionLocal() as session:
            game = session.get(GameTable, game_id)
            if game is None:
                return None

            game.board_state = board_state
            session.commit()
            session.refresh(game)
            return self._to_dict(game)

    # Actualiza si una partida sigue activa usando ORM.
    def update_active_state(self, game_id: int, active: bool) -> dict | None:
        with SessionLocal() as session:
            game = session.get(GameTable, game_id)
            if game is None:
                return None

            game.active = active
            session.commit()
            session.refresh(game)
            return self._to_dict(game)

    # Borra una partida usando ORM.
    def delete_game(self, game_id: int) -> bool:
        with SessionLocal() as session:
            game = session.get(GameTable, game_id)
            if game is None:
                return False

            session.delete(game)
            session.commit()
            return True
