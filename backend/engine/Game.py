from __future__ import annotations
from backend.engine.BoardMutable import BoardMutable
from backend.engine.Piece import *
from backend.engine.AllPiece import *

class Game:
    # Constructor de la partida y su tablero
    def __init__(self):
        self.__id: int = 0
        self.board = BoardMutable()
        self.active = False
        self.turn = PieceColor.BLANCA
        self.history = []
        self.board.attach_history(self.history)
        

    # Comenzar partida y colocar piezas en el tablero 
    def start_game(self):
        self.__id += 1
        self.board.reset()
        self.active = True
        self.turn = PieceColor.BLANCA
        self.history.clear()

        # --- Pawns ---
        for i in range(8):
            self.board.place_piece(Pawn(PieceColor.BLANCA, i, 1), i, 1)
            self.board.place_piece(Pawn(PieceColor.NEGRA, i, 6), i, 6)

        # --- Knights ---
        self.board.place_piece(Knight(PieceColor.BLANCA, 1, 0), 1, 0)
        self.board.place_piece(Knight(PieceColor.BLANCA, 6, 0), 6, 0)
        self.board.place_piece(Knight(PieceColor.NEGRA, 1, 7), 1, 7)
        self.board.place_piece(Knight(PieceColor.NEGRA, 6, 7), 6, 7)

        # --- Bishops ---
        self.board.place_piece(Bishop(PieceColor.BLANCA, 2, 0), 2, 0)
        self.board.place_piece(Bishop(PieceColor.BLANCA, 5, 0), 5, 0)
        self.board.place_piece(Bishop(PieceColor.NEGRA, 2, 7), 2, 7)
        self.board.place_piece(Bishop(PieceColor.NEGRA, 5, 7), 5, 7)

        # --- Rooks ---
        self.board.place_piece(Rook(PieceColor.BLANCA, 0, 0), 0, 0)
        self.board.place_piece(Rook(PieceColor.BLANCA, 7, 0), 7, 0)
        self.board.place_piece(Rook(PieceColor.NEGRA, 0, 7), 0, 7)
        self.board.place_piece(Rook(PieceColor.NEGRA, 7, 7), 7, 7)

        # --- Queens ---
        self.board.place_piece(Queen(PieceColor.BLANCA, 3, 0), 3, 0)
        self.board.place_piece(Queen(PieceColor.NEGRA, 3, 7), 3, 7)

        # --- Kings ---
        self.board.place_piece(King(PieceColor.BLANCA, 4, 0), 4, 0)
        self.board.place_piece(King(PieceColor.NEGRA, 4, 7), 4, 7)

    def _enemy_color(self, color: PieceColor) -> PieceColor:
        return PieceColor.NEGRA if color == PieceColor.BLANCA else PieceColor.BLANCA

    def _resolve_status_color(self, color: PieceColor | None = None) -> PieceColor:
        if color is not None:
            return PieceColor.coerce(color)

        current_king = self.board.find_king(self.turn)
        if current_king is not None:
            return self.turn

        white_king = self.board.find_king(PieceColor.BLANCA)
        black_king = self.board.find_king(PieceColor.NEGRA)
        if white_king is None and black_king is not None:
            return PieceColor.NEGRA
        if black_king is None and white_king is not None:
            return PieceColor.BLANCA
        return self.turn

    def is_in_check(self, color: PieceColor) -> bool:
        king = self.board.find_king(color)
        if king is None:
            return False
        if not isinstance(king, King):
            return False
        return king.is_in_check(self.board)

    def _is_castle_attempt(self, piece: Piece, to_x: int, to_y: int) -> bool:
        return isinstance(piece, King) and piece.y == to_y and abs(to_x - piece.x) == 2

    def _find_castle_rook(self, king: King, to_x: int) -> Rook | None:
        rook_x = 7 if to_x > king.x else 0
        rook = self.board.get_piece(rook_x, king.y)
        if isinstance(rook, Rook) and rook.piece_color == king.piece_color:
            return rook
        return None

    def _simulate_standard_move(self, piece: Piece, to_x: int, to_y: int) -> bool:
        from_x, from_y = piece.x, piece.y
        piece_state = piece.has_moved
        captured_piece = self.board.get_piece(to_x, to_y)
        board_state = self.board.snapshot_auxiliary_state()

        self.board.move_piece(from_x, from_y, to_x, to_y)
        in_check = self.is_in_check(piece.piece_color)

        piece.x = from_x
        piece.y = from_y
        piece.restore_move_state(piece_state)
        if captured_piece is not None and captured_piece not in self.board._board:
            self.board._board.append(captured_piece)
        self.board.restore_auxiliary_state(board_state)
        return in_check

    def _simulate_en_passant(self, pawn: Pawn, to_x: int, to_y: int) -> bool:
        from_x, from_y = pawn.x, pawn.y
        pawn_state = pawn.has_moved
        captured_piece = self.board.get_piece(to_x, pawn.y)
        board_state = self.board.snapshot_auxiliary_state()

        self.board.en_passant(pawn, to_x, to_y, record_history=False)
        in_check = self.is_in_check(pawn.piece_color)

        pawn.x = from_x
        pawn.y = from_y
        pawn.restore_move_state(pawn_state)
        if captured_piece is not None and captured_piece not in self.board._board:
            self.board._board.append(captured_piece)
        self.board.restore_auxiliary_state(board_state)
        return in_check

    def _simulate_castle(self, king: King, rook: Rook) -> bool:
        king_from = (king.x, king.y)
        rook_from = (rook.x, rook.y)
        king_state = king.has_moved
        rook_state = rook.has_moved
        board_state = self.board.snapshot_auxiliary_state()

        self.board.castle(king, rook, record_history=False)
        in_check = self.is_in_check(king.piece_color)

        king.x, king.y = king_from
        rook.x, rook.y = rook_from
        king.restore_move_state(king_state)
        rook.restore_move_state(rook_state)
        self.board.restore_auxiliary_state(board_state)
        return in_check

    def _is_legal_move(self, piece: Piece, to_x: int, to_y: int, enforce_turn: bool = True) -> bool:
        if enforce_turn and piece.piece_color != self.turn:
            return False

        try:
            if self._is_castle_attempt(piece, to_x, to_y):
                rook = self._find_castle_rook(piece, to_x)
                if rook is None:
                    return False
                return not self._simulate_castle(piece, rook)

            if isinstance(piece, Pawn) and self.board.has_en_passant_capture(piece, to_x, to_y):
                return not self._simulate_en_passant(piece, to_x, to_y)

            if not piece.move(to_x, to_y, self.board):
                return False
            return not self._simulate_standard_move(piece, to_x, to_y)
        except (IndexError, ValueError):
            return False

    def _has_any_legal_move(self, color: PieceColor) -> bool:
        for piece in self.board.pieces_of_color(color):
            for x in range(self.board.width):
                for y in range(self.board.height):
                    if self._is_legal_move(piece, x, y, enforce_turn=False):
                        return True
        return False
        
    # Realizar un movimiento según reglas
    def make_move(self, piece: Piece, to_x: int, to_y: int) -> bool:

        # Partida activa
        if not self.active:
            return False
        
        # Guardar origen antes de realizar el movimiento
        from_x, from_y = piece.x, piece.y

        # Turno del color correcto
        if not self._is_legal_move(piece, to_x, to_y):
            return False

        if self._is_castle_attempt(piece, to_x, to_y):
            rook = self._find_castle_rook(piece, to_x)
            if rook is None:
                return False
            self.board.castle(piece, rook)
        elif isinstance(piece, Pawn) and self.board.has_en_passant_capture(piece, to_x, to_y):
            self.board.en_passant(piece, to_x, to_y)
        else:
            self.board.move_piece(from_x, from_y, to_x, to_y)
            self.history.append({"Piece": piece, "from": (from_x, from_y), "to": (to_x, to_y)})

        # Turno del siguiente jugador
        self.next_turn()

        return True
    
    def promote_pawn(self, pawn: Pawn, new_type: type):
        if not isinstance(pawn, Pawn):
            raise ValueError("Solo se puede promocionar un Pawn")
        if not pawn.can_promote():
            return None
        
        # Comprobar tipo permitido
        if new_type not in (Queen, Rook, Bishop, Knight):
            raise ValueError("Tipo de pieza inválido para promoción")
        
        # Crear nueva pieza y reemplazar en el tablero
        promoted_piece = new_type(pawn.piece_color, pawn.x, pawn.y)
        self.board.remove_piece(pawn)
        self.board.place_piece(promoted_piece, promoted_piece.x, promoted_piece.y)
        return promoted_piece

    # Pasar turnos de jugador a jugador
    def next_turn(self):
        self.board.advance_turn()
        if self.turn == PieceColor.BLANCA:
            self.turn = PieceColor.NEGRA
        else:
            self.turn = PieceColor.BLANCA

    # Fin de partida en jaque mate
    def checkmate(self, color: PieceColor | None = None) -> bool:
        player_color = self._resolve_status_color(color)

        if not self.is_in_check(player_color):
            return False
        if self._has_any_legal_move(player_color):
            return False

        self.active = False
        return True

    def stalemate(self, color: PieceColor | None = None) -> bool:
        player_color = self._resolve_status_color(color)

        if self.is_in_check(player_color):
            return False
        if self._has_any_legal_move(player_color):
            return False

        self.active = False
        return True

    def draw(self):
        self.active = False

    def resign(self, color: str = "blanca"):
        self.active = False
        self.history.append({"result": "resign", "color": color})
        return True
    
    # Historial de movimientos de la partida
    def movement_history(self):
        return self.history
