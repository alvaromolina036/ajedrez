from __future__ import annotations
from backend.engine.Piece import *
from typing import Type

# Pawn
class Pawn(Piece):

    def __init__(self, color: PieceColor, x: int, y: int):
        super().__init__(color, x, y)
        self._has_moved = False

    @property
    def has_moved(self) -> bool:
        return self._has_moved

    def mark_as_moved(self):
        self._has_moved = True

    def restore_move_state(self, has_moved: bool):
        self._has_moved = has_moved

    def move(self, x: int, y: int, board: BoardReadOnly) -> bool:
        board.limits(x, y)

        dx = x - self.x
        dy = y - self.y
        
        # Dirección según color
        pawn_direction = 1 if self.piece_color == PieceColor.BLANCA else -1
        destino = board.get_piece(x, y)

        # Avance de 1 casilla
        if dx == 0 and dy == pawn_direction:
            if destino is None:
                return True

        # Avance inicial de 2 casillas
        if dx == 0 and dy == 2 * pawn_direction:
            start_row = 1 if self.piece_color == PieceColor.BLANCA else 6
            if not self.has_moved and self.y == start_row:
                intermediate_y = self.y + pawn_direction
                if board.get_piece(self.x, intermediate_y) is None and destino is None:
                    return True

        # Captura diagonal
        if abs(dx) == 1 and dy == pawn_direction:
            if destino is not None and destino.piece_color != self.piece_color:
                return True

        return False

    def attacks_square(self, x: int, y: int, board: BoardReadOnly) -> bool:
        board.limits(x, y)
        dx = x - self.x
        dy = y - self.y
        pawn_direction = 1 if self.piece_color == PieceColor.BLANCA else -1
        return abs(dx) == 1 and dy == pawn_direction

    # Pawn ha llegado a la última fila y puede promocionar
    def can_promote(self) -> bool:
        if self.piece_color == PieceColor.BLANCA and self.y == 7:
            return True
        if self.piece_color == PieceColor.NEGRA and self.y == 0:
            return True
        return False
       
    # Pawn puede capturar al paso (pendiente de implementar)
    def can_en_passant(self) -> bool:
        pass

# Knight
class Knight(Piece):

    def __init__(self, color: PieceColor, x: int, y: int):
        super().__init__(color, x, y)

    def move(self, x: int, y: int, board: BoardReadOnly) -> bool:
        board.limits(x, y)

        dx = abs(x - self.x)
        dy = abs(y - self.y)

        if not ((dx == 2 and dy == 1) or (dx == 1 and dy == 2)):
            return False
        
        destino = board.get_piece(x, y)
        return destino is None or destino.piece_color != self.piece_color
        
# Bishop
class Bishop(Piece):

    def __init__(self, color: PieceColor, x: int, y: int):
        super().__init__(color, x, y)

    def move(self, x: int, y: int, board: BoardReadOnly) -> bool:
        board.limits(x, y)
        dx = x - self.x
        dy = y - self.y

        if abs(dx) != abs(dy):
            return False
        if not board.path_clear(self.x, self.y, x, y):
            return False
        
        destino = board.get_piece(x, y)
        return destino is None or destino.piece_color != self.piece_color
        
# Rook
class Rook(Piece):

    def __init__(self, color: PieceColor, x: int, y: int):
        super().__init__(color, x, y)
        self._has_moved = False

    @property
    def has_moved(self) -> bool:
        return self._has_moved

    def mark_as_moved(self):
        self._has_moved = True

    def restore_move_state(self, has_moved: bool):
        self._has_moved = has_moved

    def move(self, x: int, y: int, board: BoardReadOnly) -> bool:
        board.limits(x, y)
        dx = x - self.x
        dy = y - self.y

        if dx != 0 and dy != 0:
            return False
        if not board.path_clear(self.x, self.y, x, y):
            return False
        
        destino = board.get_piece(x, y)
        return destino is None or destino.piece_color != self.piece_color
        
# Queen
class Queen(Piece):

    def __init__(self, color: PieceColor, x: int, y: int):
        super().__init__(color, x, y)

    def move(self, x: int, y: int, board: BoardReadOnly) -> bool:
        board.limits(x, y)
        dx = x - self.x
        dy = y - self.y

        if not (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
            return False
        if not board.path_clear(self.x, self.y, x, y):
            return False
        
        destino = board.get_piece(x, y)
        return destino is None or destino.piece_color != self.piece_color

# King
class King(Piece):

    def __init__(self, color: PieceColor, x: int, y: int):
        super().__init__(color, x, y)
        self._has_moved = False

    @property
    def has_moved(self) -> bool:
        return self._has_moved

    def mark_as_moved(self):
        self._has_moved = True

    def restore_move_state(self, has_moved: bool):
        self._has_moved = has_moved

    def move(self, x: int, y: int, board: BoardReadOnly) -> bool:
        board.limits(x, y)
        dx = abs(x - self.x)
        dy = abs(y - self.y)

        if dx > 1 or dy > 1:
            return False

        destino = board.get_piece(x, y)
        return destino is None or destino.piece_color != self.piece_color

    def attacks_square(self, x: int, y: int, board: BoardReadOnly) -> bool:
        board.limits(x, y)
        dx = abs(x - self.x)
        dy = abs(y - self.y)
        return dx <= 1 and dy <= 1 and (dx != 0 or dy != 0)

    def is_in_check(self, board: BoardReadOnly) -> bool:
        enemy_color = PieceColor.NEGRA if self.piece_color == PieceColor.BLANCA else PieceColor.BLANCA
        return board.is_square_attacked(self.x, self.y, enemy_color)

    def can_castle(self, rook: Rook, board: BoardReadOnly) -> bool:
        if self.has_moved or rook.has_moved:
            return False
        if self.y != rook.y:
            return False
        if not board.path_clear(self.x, self.y, rook.x, rook.y):
            return False
        if self.is_in_check(board):
            return False
        return True
