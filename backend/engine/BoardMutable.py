from __future__ import annotations
from backend.engine.BoardReadOnly import BoardReadOnly
from backend.engine.AllPiece import *
from typing import Type

class BoardMutable(BoardReadOnly):

    def __init__(self):
        super().__init__()
        self._history_ref: list | None = None
        self._turn_index = 0
        self._en_passant_pawn: Pawn | None = None
        self._en_passant_turn: int | None = None

    def attach_history(self, history: list):
        self._history_ref = history

    def reset(self):
        self._board.clear()
        self._turn_index = 0
        self.clear_en_passant()

    def advance_turn(self):
        self._turn_index += 1

    def snapshot_auxiliary_state(self):
        return (self._en_passant_pawn, self._en_passant_turn, self._turn_index)

    def restore_auxiliary_state(self, snapshot):
        self._en_passant_pawn, self._en_passant_turn, self._turn_index = snapshot

    def clear_en_passant(self):
        self._en_passant_pawn = None
        self._en_passant_turn = None

    def _record_history(self, piece: Piece, from_x: int, from_y: int, to_x: int, to_y: int):
        if self._history_ref is not None:
            self._history_ref.append({"Piece": piece, "from": (from_x, from_y), "to": (to_x, to_y)})

    def _update_en_passant_state(self, piece: Piece, origen_x: int, origen_y: int, destino_x: int, destino_y: int):
        if isinstance(piece, Pawn) and origen_x == destino_x and abs(destino_y - origen_y) == 2:
            self._en_passant_pawn = piece
            self._en_passant_turn = self._turn_index
            return
        self.clear_en_passant()

    # Colocar pieza en una posición específica
    def place_piece(self, piece: Piece, x: int, y: int):

        self.limits(x, y)

        another_piece = self.get_piece(x, y)
        if another_piece is not None:
            if another_piece.piece_color == piece.piece_color:
                raise ValueError(f"Casilla ({x}, {y}) ocupada por pieza del mismo color")
            self.remove_piece(another_piece)

        piece.x = x
        piece.y = y

        self._board.append(piece)

    # Mover pieza de una casilla a otra
    def move_piece(self, origen_x: int, origen_y: int, destino_x: int, destino_y: int, mark_moved: bool = True, track_special: bool = True):
        self.limits(destino_x, destino_y)
    
        piece = self.get_piece(origen_x, origen_y)
        if piece is None:
            raise ValueError(f"No hay pieza en ({origen_x}, {origen_y})")

        destino_piece = self.get_piece(destino_x, destino_y)
        if destino_piece is not None and destino_piece is not piece:
            self.remove_piece(destino_piece)

        piece.x = destino_x
        piece.y = destino_y
        if mark_moved:
            piece.mark_as_moved()
        if track_special:
            self._update_en_passant_state(piece, origen_x, origen_y, destino_x, destino_y)
        return destino_piece
    
    # Sacar pieza capturada
    def remove_piece(self, piece: Piece):
        if piece in self._board:
            self._board.remove(piece)

    def promote(self, pawn: Pawn, piece_type: Type[Piece]) -> Piece:
        if not pawn.can_promote():
            raise ValueError("El pawn no puede promocionar aún")
        
        if piece_type not in (Queen, Rook, Bishop, Knight):
            raise ValueError("Tipo de pieza inválido para promocionar")
        
        # Crear la nueva pieza en la posición del pawn
        nueva_pieza = piece_type(pawn.piece_color, pawn.x, pawn.y)
        
        # Reemplazar el pawn en el tablero
        self.remove_piece(pawn)
        self._board.append(nueva_pieza)
        
        return nueva_pieza

    def has_en_passant_capture(self, pawn: Pawn, target_x: int, target_y: int) -> bool:
        self.limits(target_x, target_y)

        direction = 1 if pawn.piece_color == PieceColor.BLANCA else -1
        dx = target_x - pawn.x
        dy = target_y - pawn.y

        if abs(dx) != 1 or dy != direction:
            return False
        if self.get_piece(target_x, target_y) is not None:
            return False
        if self._en_passant_pawn is None or self._en_passant_turn is None:
            return False
        if (self._turn_index - self._en_passant_turn) > 1:
            return False

        captured_piece = self.get_piece(target_x, pawn.y)
        if captured_piece is None or captured_piece is not self._en_passant_pawn:
            return False
        if captured_piece.piece_color == pawn.piece_color:
            return False
        return True

    # Pawn realiza captura al paso
    def en_passant(self, pawn: Pawn, target_x: int, target_y: int, record_history: bool = True):
        if not self.has_en_passant_capture(pawn, target_x, target_y):
            raise ValueError("No hay pawn para capturar al paso")

        from_x, from_y = pawn.x, pawn.y
        captured_piece = self.get_piece(target_x, pawn.y)

        # Capturar pawn enemigo
        self.remove_piece(captured_piece)

        # Mover el pawn
        self.move_piece(pawn.x, pawn.y, target_x, target_y, track_special=False)
        self.clear_en_passant()
        if record_history:
            self._record_history(pawn, from_x, from_y, target_x, target_y)
        return captured_piece

    # King y Rook realizan el enroque
    def castle(self, king: King, rook: Rook, record_history: bool = True):
        # Verificar condiciones básicas
        if king.piece_color != rook.piece_color:
            raise ValueError("King y Rook deben ser del mismo color")
        if king.has_moved or rook.has_moved:
            raise ValueError("King o Rook ya se han movido")
        
        if king.y != rook.y:
            raise ValueError("King y Rook no están en la misma fila")
        
        if not self.path_clear(king.x, king.y, rook.x, rook.y):
            raise ValueError("Casillas entre King y Rook no están libres")
        
        if king.is_in_check(self):
            raise ValueError("No se puede enrocar mientras el Rey está en jaque")

        # Enroque corto o largo
        step = 1 if rook.x > king.x else -1
        middle_x = king.x + step
        king_new_x = king.x + 2 * step
        rook_new_x = king.x + step
        enemy_color = PieceColor.NEGRA if king.piece_color == PieceColor.BLANCA else PieceColor.BLANCA

        if self.is_square_attacked(middle_x, king.y, enemy_color):
            raise ValueError("El Rey no puede pasar por una casilla atacada")
        if self.is_square_attacked(king_new_x, king.y, enemy_color):
            raise ValueError("El Rey no puede terminar en una casilla atacada")

        king_from = (king.x, king.y)
        rook_from = (rook.x, rook.y)

        # Mover King y Rook en el tablero
        self.move_piece(king.x, king.y, king_new_x, king.y, mark_moved=False, track_special=False)
        self.move_piece(rook.x, rook.y, rook_new_x, rook.y, mark_moved=False, track_special=False)

        # Marcar que ya se han movido
        king.mark_as_moved()
        rook.mark_as_moved()
        self.clear_en_passant()
        if record_history:
            self._record_history(king, king_from[0], king_from[1], king_new_x, king.y)
            self._record_history(rook, rook_from[0], rook_from[1], rook_new_x, rook.y)
