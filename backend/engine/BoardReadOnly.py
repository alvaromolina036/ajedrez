from __future__ import annotations
from backend.engine.Piece import *
from backend.engine.PieceInfo import *

class BoardReadOnly:

    # Constructor del tablero para SOLO LECTURA, con lista de piezas
    def __init__(self):
        self._board: list[Piece] = []
        self.width = 8
        self.height = 8

    # Verificar si una coordenada está dentro del tablero
    def limits(self, x: int, y: int):
        if x < 0 or x >= self.width:
            raise IndexError(f"Posición {x}x fuera del tablero")
        if y < 0 or y >= self.height:
            raise IndexError(f"Posición {y}y fuera del tablero")

    # Devolver la pieza que ocupa la posición solicitada
    def get_piece(self, x: int, y: int) -> Piece | None:
        for piece in self._board:
            if piece.x == x and piece.y == y:
                return piece
        return None

    def pieces_of_color(self, color: PieceColor) -> list[Piece]:
        return [piece for piece in self._board if piece.piece_color == color]

    def find_king(self, color: PieceColor):
        for piece in self._board:
            if piece.__class__.__name__ == "King" and piece.piece_color == color:
                return piece
        return None
    
    def path_clear(self, origen_x: int, origen_y: int, destino_x: int, destino_y: int) -> bool:
        nueva_x = destino_x - origen_x
        nueva_y = destino_y - origen_y

        step_x = 0 if nueva_x == 0 else int(nueva_x / abs(nueva_x))
        step_y = 0 if nueva_y == 0 else int(nueva_y / abs(nueva_y))

        current_x = origen_x + step_x
        current_y = origen_y + step_y

        while (current_x, current_y) != (destino_x, destino_y):
            if self.get_piece(current_x, current_y) is not None:
                return False
            
            current_x += step_x
            current_y += step_y
        return True

    def is_square_attacked(self, x: int, y: int, by_color: PieceColor) -> bool:
        self.limits(x, y)
        for piece in self._board:
            if piece.piece_color != by_color:
                continue
            if piece.attacks_square(x, y, self):
                return True
        return False

    def has_en_passant_capture(self, pawn: Piece, target_x: int, target_y: int) -> bool:
        return False

    def board_position(self) -> list[PieceInfo]:
        pieceinfo_list: list[PieceInfo] = []

        for piece in self._board:
            pieceinfo_list.append(PieceInfo(x = piece.x, y = piece.y, color = piece.piece_color, tipo = piece.__class__.__name__))
        return pieceinfo_list
