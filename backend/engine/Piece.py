from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.engine.BoardReadOnly import BoardReadOnly

class PieceColor(Enum):
    NEGRA = "NEGRA"
    BLANCA = "BLANCA"

    @classmethod
    def coerce(cls, color: PieceColor | str) -> PieceColor:
        if isinstance(color, cls):
            return color
        if isinstance(color, str):
            normalized = color.upper()
            for member in cls:
                if member.value == normalized:
                    return member
        raise ValueError(f"Color de pieza inválido: {color!r}")

class Piece(ABC):

    # Constructor de las piezas con su color y posición
    def __init__(self, color: PieceColor | str, x: int, y: int):
        self.color: PieceColor = PieceColor.coerce(color)
        self.x = x
        self.y = y

    # Color de la pieza (blanca o negra)
    @property
    def piece_color(self) -> PieceColor:
        return self.color
    
    # Colocar posición de la pieza (x / y)
    @property
    def position(self):
        return self.x, self.y

    @property
    def has_moved(self) -> bool:
        return False

    def mark_as_moved(self):
        pass

    def restore_move_state(self, has_moved: bool):
        pass

    # Comprobar si un movimiento es válido
    @abstractmethod
    def move(self, x: int, y: int, board: BoardReadOnly) -> bool:
        pass

    def attacks_square(self, x: int, y: int, board: BoardReadOnly) -> bool:
        return self.move(x, y, board)
