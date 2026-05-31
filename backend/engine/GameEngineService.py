from __future__ import annotations
from backend.engine.Game import Game
from backend.engine.Movement import Movement
from backend.engine.PieceInfo import PieceInfo
from backend.engine.Piece import PieceColor
from backend.engine.AllPiece import Bishop, King, Knight, Pawn, Queen, Rook

class GameEngineService:
    def __init__(self):
        self.game = Game()

    def start_game(self):
        # Iniciar nueva partida
        self.game.start_game()
        return self.get_board()

    def make_move(self, movement: Movement) -> bool:
        piece = self.game.board.get_piece(movement.from_x, movement.from_y)
        if piece is None:
            return False
        moved = self.game.make_move(piece, movement.to_x, movement.to_y)
        return moved

    def get_board(self):
        board = []
        for piece in self.game.board.board_position():
            color = piece.color.value if hasattr(piece.color, "value") else piece.color
            board.append(PieceInfo(x=piece.x, y=piece.y, color=color, tipo=piece.tipo))
        return board

    # Devuelve estado persistible de la partida.
    def get_state(self) -> dict:
        pieces = []
        for piece in self.game.board._board:
            pieces.append({
                "x": piece.x,
                "y": piece.y,
                "color": piece.color.value,
                "tipo": piece.__class__.__name__,
                "has_moved": piece.has_moved,
            })

        return {
            "board": pieces,
            "turn": self.game.turn.value,
            "active": self.game.active,
        }

    # Reconstruye el motor desde el JSON guardado en base de datos.
    def load_state(self, state: dict):
        piece_classes = {
            "Pawn": Pawn,
            "Knight": Knight,
            "Bishop": Bishop,
            "Rook": Rook,
            "Queen": Queen,
            "King": King,
        }

        self.game.board.reset()
        self.game.history.clear()
        self.game.active = bool(state.get("active", True))
        self.game.turn = PieceColor.coerce(state.get("turn", "BLANCA"))

        for piece_data in state.get("board", []):
            piece_type = piece_data.get("tipo")
            piece_class = piece_classes.get(piece_type)
            if piece_class is None:
                continue

            piece = piece_class(
                PieceColor.coerce(piece_data["color"]),
                piece_data["x"],
                piece_data["y"],
            )
            piece.restore_move_state(bool(piece_data.get("has_moved", False)))
            self.game.board.place_piece(piece, piece.x, piece.y)
    
    def want_resign(self, color: str = "blanca"):
        # Llamar al método de Game
        result = self.game.resign(color=color)
        
        return {
            "resigned": result,
            "color": color,
            "game_active": self.game.active,
            "history": self.game.history[-1]
        }

    def get_game_status(self):
        if self.game.checkmate():
            return "checkmate"
        if self.game.stalemate():
            return "stalemate"
        if not self.game.active:
            return "draw"
        return "active"

GameController = GameEngineService
