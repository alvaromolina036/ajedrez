from __future__ import annotations
from backend.engine.PieceInfo import *
from backend.engine.Movement import *
from backend.engine.AllPiece import *
from backend.engine.Piece import *
from backend.engine.BoardReadOnly import *
from backend.engine.BoardMutable import *
from backend.engine.Game import *
from backend.engine.GameEngineService import *
import random

# -- INICIO PARTIDA NORMAL -- #

# Inicialización del tablero - Crea todas las piezas en sus posiciones correctas.
def test_start_game_initial_positions():
    game = Game()
    game.start_game()
    board = game.board.board_position()

    # Contadores de piezas por tipo y color
    piece_count = {
        "Pawn": {PieceColor.BLANCA: 0, PieceColor.NEGRA: 0},
        "Knight": {PieceColor.BLANCA: 0, PieceColor.NEGRA: 0},
        "Bishop": {PieceColor.BLANCA: 0, PieceColor.NEGRA: 0},
        "Rook": {PieceColor.BLANCA: 0, PieceColor.NEGRA: 0},
        "Queen": {PieceColor.BLANCA: 0, PieceColor.NEGRA: 0},
        "King": {PieceColor.BLANCA: 0, PieceColor.NEGRA: 0},
    }

    for piece in board:
        piece_count[piece.tipo][piece.color] += 1

    # Comprobaciones
    assert piece_count["Pawn"][PieceColor.BLANCA] == 8
    assert piece_count["Pawn"][PieceColor.NEGRA] == 8
    assert piece_count["Knight"][PieceColor.BLANCA] == 2
    assert piece_count["Knight"][PieceColor.NEGRA] == 2
    assert piece_count["Bishop"][PieceColor.BLANCA] == 2
    assert piece_count["Bishop"][PieceColor.NEGRA] == 2
    assert piece_count["Rook"][PieceColor.BLANCA] == 2
    assert piece_count["Rook"][PieceColor.NEGRA] == 2
    assert piece_count["Queen"][PieceColor.BLANCA] == 1
    assert piece_count["Queen"][PieceColor.NEGRA] == 1
    assert piece_count["King"][PieceColor.BLANCA] == 1
    assert piece_count["King"][PieceColor.NEGRA] == 1

    # Comprobar posiciones clave (ejemplos)
    assert any(p.x == 0 and p.y == 0 and p.tipo == "Rook" and p.color == PieceColor.BLANCA for p in board)
    assert any(p.x == 4 and p.y == 7 and p.tipo == "King" and p.color == PieceColor.NEGRA for p in board)
    assert any(p.x == 3 and p.y == 0 and p.tipo == "Queen" and p.color == PieceColor.BLANCA for p in board)

    print("Test de inicialización: OK")


# Conteo piezas – 16 Blancas y 16 Negras al iniciar.
def test_piece_count_start_game():
    game = Game()
    game.start_game()
    board = game.board.board_position()

    blancas = sum(1 for p in board if p.color == PieceColor.BLANCA)
    negras = sum(1 for p in board if p.color == PieceColor.NEGRA)

    assert blancas == 16, f"Se esperaban 16 piezas blancas, hay {blancas}"
    assert negras == 16, f"Se esperaban 16 piezas negras, hay {negras}"

    print("Test conteo piezas al inicio: OK")


# Turno inicial – Comienza con blancas.
def test_initial_turn():
    game = Game()
    game.start_game()

    assert game.turn == PieceColor.BLANCA, f"Turno inicial incorrecto, esperado BLANCA, hay {game.turn}"
    print("Test turno inicial: OK")


# -- MOVIMIENTOS BÁSICOS -- #

# Movimiento básico de Pawn
def test_pawn_move():
    game = Game()
    game.start_game()
    # Mover peón blanco de (0,1) a (0,2)
    piece = game.board.get_piece(0, 1)
    assert isinstance(piece, Pawn)
    moved = game.make_move(piece, 0, 2)
    assert moved, "Peón no pudo moverse una casilla hacia adelante"
    print("Test peon: OK")


# Movimiento básico de Knight
def test_knight_move():
    game = Game()
    game.start_game()
    # Mover caballo blanco de (1,0) a (2,2)
    piece = game.board.get_piece(1, 0)
    assert isinstance(piece, Knight)
    moved = game.make_move(piece, 2, 2)
    assert moved, "Caballo no pudo moverse en L"
    print("Test caballo: OK")

 
# Movimiento básico de Bishop
def test_bishop_move():
    game = Game()
    game.start_game()
    # Liberamos el camino para alfil en (2,0) -> (4,2)
    game.board.move_piece(3, 1, 3, 3)
    piece = game.board.get_piece(2, 0)
    assert isinstance(piece, Bishop)
    moved = game.make_move(piece, 4, 2)
    assert moved, "Alfil no pudo moverse en diagonal"
    print("Test alfil: OK")


# Movimiento básico de Rook
def test_rook_move():
    game = Game()
    game.start_game()
    # Liberamos camino torre (0,0) -> (0,3)
    game.board.move_piece(0, 1, 0, 3)  # mover peón
    piece = game.board.get_piece(0, 0)
    assert isinstance(piece, Rook)
    moved = game.make_move(piece, 0, 2)
    assert moved, "Torre no pudo moverse en línea recta"
    print("Test torre: OK")


# Movimiento básico de Queen
def test_queen_move():
    game = Game()
    game.start_game()
    # Liberamos camino reina (3,0) -> (3,3)
    game.board.move_piece(3, 1, 3, 3)
    piece = game.board.get_piece(3, 0)
    assert isinstance(piece, Queen)
    moved = game.make_move(piece, 3, 2)
    assert moved, "Dama no pudo moverse verticalmente"
    print("Test dama: OK")


# Movimiento básico de King
def test_king_move():
    game = Game()
    game.start_game()
    # Liberamos camino rey (4,0) -> (4,1)
    game.board.move_piece(4, 1, 4, 3)
    piece = game.board.get_piece(4, 0)
    assert isinstance(piece, King)
    moved = game.make_move(piece, 4, 1)
    assert moved, "Rey no pudo moverse una casilla"
    print("Test rey: OK")


# Movimiento fuera del tablero – debe fallar.
def test_move_out_of_bounds():
    game = Game()
    game.start_game()
    
    # Intentamos mover peón blanco fuera del tablero
    piece = game.board.get_piece(0, 1)
    assert isinstance(piece, Pawn)
    
    try:
        # Movimiento inválido (y=8 está fuera)
        moved = game.make_move(piece, 0, 8)
        assert not moved, "Movimiento fuera del tablero debería fallar"
    except IndexError:
        # También se puede lanzar IndexError según BoardReadOnly.limits
        print("Movimiento fuera del tablero: OK (IndexError capturado)")
        return

    print("Movimiento fuera del tablero: OK")


# Captura enemiga – Solo se puede capturar piezas del color contrario.
def test_capture_enemy():
    game = Game()
    game.start_game()
    
    # Movemos peón negro a (1,3) para que esté diagonal al peón blanco en (0,1)
    game.board.move_piece(1, 6, 1, 2)
    
    # Mover peón blanco (0,1) -> (1,2) para capturar diagonal
    white_pawn = game.board.get_piece(0, 1)
    moved = game.make_move(white_pawn, 1, 2)
    
    assert moved, "Peón blanco no pudo capturar peón negro"
    
    # Comprobar que el peón negro fue removido
    piece = game.board.get_piece(1, 2)
    assert piece == white_pawn, "El peón blanco no terminó en la casilla del enemigo"
    
    print("Captura enemiga: OK")


# Captura propia – Debe fallar.
def test_capture_own_piece():
    game = Game()
    game.start_game()
    
    # Liberamos torre blanca moviendo peón (0,1) -> (0,2)
    game.board.move_piece(0, 1, 0, 2)
    
    rook = game.board.get_piece(0, 0)
    
    # Intentar capturar peón blanco en (0,2)
    moved = game.make_move(rook, 0, 2)
    assert not moved, "Torre no debería capturar pieza propia"
    
    print("Captura propia: OK")

# Captura en_passant – Validar captura de pieza enemiga.
def test_en_passant():
    game = Game()
    game.start_game()
    
    # Preparar tablero para en passant:
    # Peón blanco en (4,4), peón negro avanza 2 desde (5,6) -> (5,4)
    game.board.move_piece(4, 1, 4, 4)  # Peón blanco avanzado
    game.board.move_piece(5, 6, 5, 4)  # Peón negro avanzando dos

    white_pawn = game.board.get_piece(4, 4)
    
    # Ejecutar en passant
    game.board.en_passant(white_pawn, 5, 5)
    
    # Comprobar que peón negro desapareció
    captured_piece = game.board.get_piece(5, 4)
    assert captured_piece is None, "Peón negro no fue capturado en passant"
    
    # Comprobar que peón blanco terminó en la casilla correcta
    piece = game.board.get_piece(5, 5)
    assert piece == white_pawn, "Peón blanco no terminó en la posición correcta"
    
    print("En passant: OK")


# Promoción – Devuelve True cuando Pawn llega a la última fila.
def test_can_promote():
    game = Game()
    game.start_game()

    pawn = game.board.get_piece(0, 1)
    assert isinstance(pawn, Pawn), "La pieza no es un Pawn"

    pawn.y = 7

    assert pawn.can_promote(), "can_promote() no devuelve True en última fila"
    print("can_promote(): OK")

# Promoción – Reemplaza peón por pieza válida (Queen, Rook, Bishop, Knight).
def test_promote_pawn_valid():
    game = Game()
    game.start_game()

    pawn = game.board.get_piece(0, 1)
    assert isinstance(pawn, Pawn)

    # Forzar última fila
    pawn.y = 7
    assert pawn.can_promote()

    # Promocionar a Queen
    new_piece = game.promote_pawn(pawn, Queen)

    assert isinstance(new_piece, Queen), "No se creó una Queen"
    assert new_piece.x == 0 and new_piece.y == 7, "Posición incorrecta tras promoción"

    # Verificar que el Pawn ya no está
    piece = game.board.get_piece(0, 7)
    assert not isinstance(piece, Pawn), "El Pawn no fue reemplazado"

    print("Promoción válida: OK")

# Promoción inválida – Intentar elegir otro peón o King.
def test_promote_pawn_invalid():
    game = Game()
    game.start_game()

    pawn = game.board.get_piece(0, 1)
    assert isinstance(pawn, Pawn)

    # Forzar última fila
    pawn.y = 7
    assert pawn.can_promote()

    # Intentar promocionar a King (inválido)
    try:
        game.promote_pawn(pawn, King)
        assert False, "Promoción a King debería fallar"
    except ValueError:
        pass

    # Intentar promocionar a Pawn (inválido)
    try:
        game.promote_pawn(pawn, Pawn)
        assert False, "Promoción a Pawn debería fallar"
    except ValueError:
        pass

    print("Promoción inválida: OK")

# Enroque corto – Validar condiciones.
def test_castle_short():
    game = Game()
    game.start_game()

    king = game.board.get_piece(4, 0)
    rook = game.board.get_piece(7, 0)

    # Liberar camino (quitar caballo y alfil)
    game.board.remove_piece(game.board.get_piece(5, 0))
    game.board.remove_piece(game.board.get_piece(6, 0))

    # Ejecutar enroque
    game.board.castle(king, rook)

    # Verificar posiciones finales
    new_king = game.board.get_piece(6, 0)
    new_rook = game.board.get_piece(5, 0)

    assert isinstance(new_king, King), "Rey no terminó en posición correcta"
    assert isinstance(new_rook, Rook), "Torre no terminó en posición correcta"

    print("Enroque corto: OK")

# Enroque largo – Validar condiciones
def test_castle_long():
    game = Game()
    game.start_game()

    king = game.board.get_piece(4, 0)
    rook = game.board.get_piece(0, 0)

    # Liberar camino (quitar caballo, alfil y dama)
    game.board.remove_piece(game.board.get_piece(1, 0))
    game.board.remove_piece(game.board.get_piece(2, 0))
    game.board.remove_piece(game.board.get_piece(3, 0))

    # Ejecutar enroque
    game.board.castle(king, rook)

    # Verificar posiciones finales
    new_king = game.board.get_piece(2, 0)
    new_rook = game.board.get_piece(3, 0)

    assert isinstance(new_king, King), "Rey no terminó en posición correcta"
    assert isinstance(new_rook, Rook), "Torre no terminó en posición correcta"

    print("Enroque largo: OK")

# Enroque bloqueado – Casillas intermedias ocupadas.
def test_castle_blocked():
    game = Game()
    game.start_game()

    king = game.board.get_piece(4, 0)
    rook = game.board.get_piece(7, 0)

    # NO liberamos el camino (hay piezas en medio)

    try:
        game.board.castle(king, rook)
        assert False, "El enroque debería fallar si hay piezas en medio"
    except Exception:
        print("Enroque bloqueado: OK")

# Enroque con Rey en jaque – Debe fallar.
def test_castle_while_in_check():
    game = Game()
    game.start_game()

    king = game.board.get_piece(4, 0)
    rook = game.board.get_piece(7, 0)

    # Liberar camino para enroque
    game.board.remove_piece(game.board.get_piece(5, 0))
    game.board.remove_piece(game.board.get_piece(6, 0))
    for y in range(1, 8):
        piece = game.board.get_piece(4, y)
        if piece:
            game.board.remove_piece(piece)

    # Colocar torre enemiga que da jaque al rey
    enemy_rook = Rook(PieceColor.NEGRA, 4, 7)
    game.board.place_piece(enemy_rook, 4, 7)

    # Intentar enroque
    try:
        game.board.castle(king, rook)
        assert False, "No debería permitir enroque estando en jaque"
    except ValueError:
        print("Enroque en jaque: OK")
 
# Enroque con pieza ya movida – Debe fallar.
def test_castle_piece_moved():
    game = Game()
    game.start_game()

    king = game.board.get_piece(4, 0)
    rook = game.board.get_piece(7, 0)

    # Liberar camino
    game.board.remove_piece(game.board.get_piece(5, 0))
    game.board.remove_piece(game.board.get_piece(6, 0))

    # Simular que el rey ya se movió moviéndolo a otra casilla y luego devolviéndolo
    game.board.move_piece(king.x, king.y, 4, 1)  # Rey se mueve "una vez"
    game.board.move_piece(king.x, king.y, 4, 0)  # Rey vuelve a la posición original

    # Ahora castle debería fallar, porque _has_moved se actualiza internamente al moverlo
    try:
        game.board.castle(king, rook)
        assert False, "No debería permitir enroque si el rey ya se movió"
    except ValueError:
        print("Enroque con rey ya movido (simulado moviendo la pieza): OK")


# -- JAQUE / JAQUE MATE / FIN DE PARTIDA -- #
 
# Jaque – Detecta correctamente jaque a King.
def test_check_detection():
    game = Game()
    game.start_game()

    king = game.board.get_piece(4, 0)
    assert isinstance(king, King)

    # Limpiar columna para que la torre negra tenga línea directa
    for y in range(1, 8):
        piece = game.board.get_piece(4, y)
        if piece:
            game.board.remove_piece(piece)

    # Colocar torre negra en misma columna que el rey
    enemy_rook = Rook(PieceColor.NEGRA, 4, 7)
    game.board.place_piece(enemy_rook, 4, 7)

    # Comprobar que el rey blanco está en jaque
    assert king.is_in_check(game.board), "El rey no detecta jaque correctamente"

    print("Jaque detectado correctamente: OK")
 
# Movimiento que deja al King en jaque – Debe rechazarse.
def test_move_leaves_king_in_check():
    game = Game()
    game.start_game()

    king = game.board.get_piece(4, 0)  # Rey blanco

    # Limpiar columna 4 para que la torre negra tenga línea directa
    for y in range(1, 8):  # hasta 7 incluido
        piece = game.board.get_piece(4, y)
        if piece:
            game.board.remove_piece(piece)

    # Colocar torre negra
    enemy_rook = Rook(PieceColor.NEGRA, 4, 7)
    game.board.place_piece(enemy_rook, 4, 7)

    # Intentar mover un peón que deje al rey en jaque
    pawn = game.board.get_piece(3, 1)
    moved = game.make_move(pawn, 3, 2)

    assert not moved, "Movimiento que deja al rey en jaque no fue rechazado"
    print("Movimiento que deja al Rey en jaque: OK")
 
# Jaque mate – checkmate() devuelve True y termina partida.
def test_checkmate():
    game = Game()
    game.start_game()

    # Limpiar tablero
    for piece in game.board._board[:]:
        game.board.remove_piece(piece)

    # Colocar rey negro
    king = King(PieceColor.NEGRA, 0, 0)
    game.board.place_piece(king, 0, 0)

    # Mate básico: dama apoyada por rey
    queen = Queen(PieceColor.BLANCA, 1, 1)
    white_king = King(PieceColor.BLANCA, 2, 2)
    game.board.place_piece(queen, 1, 1)
    game.board.place_piece(white_king, 2, 2)

    game.turn = PieceColor.NEGRA

    assert game.checkmate(), "Jaque mate no detectado"
    assert not game.active, "Partida no terminó tras jaque mate"
    print("Jaque mate: OK")
 
# Ahogado – stalemate() detectado y termina partida.
def test_stalemate():
    game = Game()
    game.start_game()

    # Limpiar tablero
    for piece in game.board._board[:]:
        game.board.remove_piece(piece)

    # Colocar rey negro atrapado sin estar en jaque
    king = King(PieceColor.NEGRA, 0, 0)
    game.board.place_piece(king, 0, 0)

    # Ahogado clásico: la dama encierra, el rey apoya, pero no hay jaque
    queen = Queen(PieceColor.BLANCA, 1, 2)
    white_king = King(PieceColor.BLANCA, 2, 1)
    game.board.place_piece(queen, 1, 2)
    game.board.place_piece(white_king, 2, 1)

    game.turn = PieceColor.NEGRA

    assert game.stalemate(), "Ahogado no detectado"
    assert not game.active, "Partida no terminó tras ahogado"
    print("Ahogado: OK")

# Tablas por acuerdo – draw() detectado y termina juego.
def test_draw():
    game = Game()
    game.start_game()
    game.draw()
    assert not game.active, "Partida no terminó tras tablas"
    print("Tablas por acuerdo: OK")

# Rendición – resign() termina partida y registra jugador.
def test_resign():
    controller = GameController()
    controller.start_game()
    
    # Rendición del jugador blanco
    result = controller.want_resign("blanca")
    
    # Comprobaciones
    assert not result["game_active"], "Partida no terminó tras rendición"
    assert result["resigned"] is True, "Rendición no fue exitosa"
    assert result["history"]["result"] == "resign" and result["history"]["color"] == "blanca", "Rendición no registrada correctamente"
    
    print("Petición de rendición: OK")


# -- HISTORIAL DE MOVIMIENTOS -- #
 
# Historial básico – movement_history() registra origen, destino y pieza.
def test_movement_history_basic():
    game = Game()
    game.start_game()

    # Mover peón blanco de (0,1) a (0,3)
    pawn = game.board.get_piece(0, 1)
    moved = game.make_move(pawn, 0, 3)
    assert moved, "Movimiento no válido"

    history = game.movement_history()
    last = history[-1]

    assert last["Piece"] == pawn, "Historial no registra la pieza correcta"
    assert last["from"] == (0,1) and last["to"] == (0,3), "Historial no registra correctamente origen/destino"
    
    print("Historial básico: OK")

# Historial especial – movimientos como enroque, promoción y en_passant registrados correctamente.
def test_movement_history_castle():
    game = Game()
    game.start_game()

    # Limpiar camino para enroque
    game.board.remove_piece(game.board.get_piece(5,0))
    game.board.remove_piece(game.board.get_piece(6,0))

    king = game.board.get_piece(4,0)
    rook = game.board.get_piece(7,0)

    # Realizar enroque corto
    game.board.castle(king, rook)

    history = game.movement_history()

    # Se registran dos movimientos (rey y torre)
    last_king_move = history[0]
    last_rook_move = history[-1]

    assert isinstance(last_king_move["Piece"], type(king)), "Historial no registra rey en enroque"
    assert isinstance(last_rook_move["Piece"], type(rook)), "Historial no registra torre en enroque"
    print("Historial enroque: OK")


# -- COMPROBACIÓN MOVIMIENTO DE LAS PIEZAS -- #
 
# Knight – Movimientos en “L” bloqueados por piezas amigas o enemigas.
def test_knight_blocked():
    game = Game()
    game.start_game()

    # Limpiar tablero
    for p in game.board._board[:]:
        game.board.remove_piece(p)

    knight = Knight(PieceColor.BLANCA, 4,4)
    game.board.place_piece(knight,4,4)

    # Bloqueo con pieza amiga en destino válido
    friend = Pawn(PieceColor.BLANCA, 5,6)
    game.board.place_piece(friend,5,6)

    moved = game.make_move(knight,5,6)
    assert not moved, "Knight no debería capturar pieza amiga"

    # Colocar enemigo en otro destino válido
    enemy = Pawn(PieceColor.NEGRA, 6,5)
    game.board.place_piece(enemy,6,5)

    moved = game.make_move(knight,6,5)
    assert moved, "Knight debería poder capturar enemigo"
    print("Knight bloqueos: OK")

# Bishop – No salta sobre piezas.
def test_bishop_block():
    game = Game()
    game.start_game()

    for p in game.board._board[:]:
        game.board.remove_piece(p)

    bishop = Bishop(PieceColor.BLANCA, 2,2)
    game.board.place_piece(bishop,2,2)

    # Bloqueo en diagonal
    blocking = Pawn(PieceColor.BLANCA, 3,3)
    game.board.place_piece(blocking,3,3)

    moved = game.make_move(bishop,4,4)
    assert not moved, "Bishop no puede saltar piezas amigas"

    game.board.remove_piece(blocking)
    enemy = Pawn(PieceColor.NEGRA,3,3)
    game.board.place_piece(enemy,3,3)
    moved = game.make_move(bishop,4,4)
    assert not moved, "Bishop no puede saltar piezas enemigas"
    print("Bishop bloqueos: OK")

# Rook – No salta sobre piezas.
def test_rook_block():
    game = Game()
    game.start_game()

    for p in game.board._board[:]:
        game.board.remove_piece(p)

    rook = Rook(PieceColor.BLANCA,0,0)
    game.board.place_piece(rook,0,0)

    blocking = Pawn(PieceColor.BLANCA,0,1)
    game.board.place_piece(blocking,0,1)

    moved = game.make_move(rook,0,3)
    assert not moved, "Rook no puede saltar piezas amigas"

    game.board.remove_piece(blocking)
    enemy = Pawn(PieceColor.NEGRA,0,1)
    game.board.place_piece(enemy,0,1)

    moved = game.make_move(rook,0,3)
    assert not moved, "Rook no puede saltar piezas enemigas"
    print("Rook bloqueos: OK")

# Queen – Combina diagonales y rectas con bloqueos respetados.
def test_queen_block():
    game = Game()
    game.start_game()

    for p in game.board._board[:]:
        game.board.remove_piece(p)

    queen = Queen(PieceColor.BLANCA,3,3)
    game.board.place_piece(queen,3,3)

    # Bloqueo diagonal
    game.board.place_piece(Pawn(PieceColor.BLANCA,4,4),4,4)
    moved = game.make_move(queen,5,5)
    assert not moved, "Queen no puede saltar piezas diagonales"

    game.board.remove_piece(game.board.get_piece(4,4))
    # Bloqueo recto
    game.board.place_piece(Pawn(PieceColor.BLANCA,3,5),3,5)
    moved = game.make_move(queen,3,6)
    assert not moved, "Queen no puede saltar piezas rectas"
    print("Queen bloqueos: OK")
    
# King – Nunca puede moverse a casilla bajo ataque.
def test_king_safe():
    game = Game()
    game.start_game()
    for p in game.board._board[:]:
        game.board.remove_piece(p)

    king = King(PieceColor.BLANCA,4,4)
    game.board.place_piece(king,4,4)

    enemy_rook = Rook(PieceColor.NEGRA,4,7)
    game.board.place_piece(enemy_rook,4,7)

    moved = game.make_move(king,4,5)
    assert not moved, "King no puede moverse a casilla atacada"
    print("King seguridad: OK")

# Peones avanzados – No pueden avanzar dos casillas después de mover.
def test_pawn_double_move():
    game = Game()
    game.start_game()
    for p in game.board._board[:]:
        game.board.remove_piece(p)

    pawn = Pawn(PieceColor.BLANCA,0,1)
    game.board.place_piece(pawn,0,1)

    # Primer movimiento doble permitido
    moved = game.make_move(pawn,0,3)
    assert moved, "Primer avance doble debe ser válido"

    # Segundo movimiento doble debe fallar
    moved = game.make_move(pawn,0,5)
    assert not moved, "Peón no puede mover dos casillas tras moverse"
    print("Peón avance doble: OK")

# Peones – en_passant solo válido inmediatamente después del avance doble rival.
def test_en_passant_timing():
    game = Game()
    game.start_game()
    for p in game.board._board[:]:
        game.board.remove_piece(p)

    wp = Pawn(PieceColor.BLANCA,4,4)
    bp = Pawn(PieceColor.NEGRA,5,6)
    game.board.place_piece(wp,4,4)
    game.board.place_piece(bp,5,6)

    # Peón negro avanza doble
    game.board.move_piece(5,6,5,4)

    # Turno blanco: captura en_passant válido
    game.board.en_passant(wp,5,5)
    assert game.board.get_piece(5,5) == wp, "en_passant válido falló"

    # Reiniciamos el escenario y dejamos pasar el turno para invalidarlo
    for p in game.board._board[:]:
        game.board.remove_piece(p)

    wp2 = Pawn(PieceColor.BLANCA,4,4)
    bp2 = Pawn(PieceColor.NEGRA,5,6)
    game.board.place_piece(wp2,4,4)
    game.board.place_piece(bp2,5,6)
    game.board.move_piece(5,6,5,4)
    game.next_turn()  # turno negro
    game.next_turn()  # turno blanco

    try:
        # Intento en_passant inválido
        game.board.en_passant(wp2,5,5)
        assert False, "en_passant debe fallar después de turno"
    except Exception:
        print("en_passant temporización: OK")

# -- ESCENARIOS COMBINADOS -- #

# Escenarios combinados – jaque + enroque ilegal.
def test_check_and_illegal_castle():
    game = Game()
    game.start_game()

    # Limpiar tablero y colocar rey y torre blanca
    for p in game.board._board[:]:
        game.board.remove_piece(p)

    king = King(PieceColor.BLANCA,4,0)
    rook = Rook(PieceColor.BLANCA,7,0)
    game.board.place_piece(king,4,0)
    game.board.place_piece(rook,7,0)

    # Liberar camino entre rey y torre
    # No hay piezas intermedias

    # Colocar torre enemiga que da jaque al rey
    enemy_rook = Rook(PieceColor.NEGRA,4,7)
    game.board.place_piece(enemy_rook,4,7)

    # Intentar enroque corto (debe fallar)
    try:
        game.board.castle(king, rook)
        assert False, "No debería permitir enroque cuando el rey está en jaque"
    except Exception:
        print("Escenario combinado: enroque ilegal en jaque detectado correctamente")

# Escenarios combinados – jaque mate con posibilidad de captura de otra pieza - Rey protegido primero.
def test_checkmate_with_escape_option():
    game = Game()
    game.start_game()

    # Limpiar tablero para controlar la situación
    for p in game.board._board[:]:
        game.board.remove_piece(p)

    # Colocar rey blanco
    king = King(PieceColor.BLANCA, 4, 0)
    game.board.place_piece(king, 4, 0)

    # Colocar torre negra dando jaque horizontal
    enemy_rook = Rook(PieceColor.NEGRA, 7, 0)
    game.board.place_piece(enemy_rook, 7, 0)

    # Colocar torre amiga que puede capturar la torre enemiga
    defending_rook = Rook(PieceColor.BLANCA, 7, 1)
    game.board.place_piece(defending_rook, 7, 1)

    # Verificamos que aún no es jaque mate porque hay captura legal
    assert not game.checkmate(), "No debe ser jaque mate, pieza puede capturar atacante"

    # Realizamos captura de torre enemiga
    moved = game.make_move(defending_rook, 7, 0)
    assert moved, "La pieza defensora debería poder capturar al atacante"

    # Ahora rey ya no está en jaque, tampoco jaque mate
    assert not game.checkmate(), "Después de capturar atacante, no debe haber jaque mate"

    print("Escenario combinado: jaque con posible captura – OK")

# Escenarios combinados – promoción en jaque - nueva pieza sigue reglas normales.
def test_promotion_under_check():
    game = Game()
    game.start_game()

    # Limpiar tablero para controlar situación
    for p in game.board._board[:]:
        game.board.remove_piece(p)

    # Colocar rey blanco en jaque
    king = King(PieceColor.BLANCA, 4, 5)
    game.board.place_piece(king, 4, 5)

    # Colocar peón blanco listo para promocionar capturando la pieza que da jaque
    pawn = Pawn(PieceColor.BLANCA, 5, 6)
    game.board.place_piece(pawn, 5, 6)

    # Torre negra dando jaque al rey blanco
    enemy_rook = Rook(PieceColor.NEGRA, 4, 7)
    game.board.place_piece(enemy_rook, 4, 7)

    # Captura de promoción que elimina el jaque
    moved = game.make_move(pawn, 4, 7)
    assert moved, "El peón debería poder capturar y promocionar resolviendo el jaque"
    assert not game.is_in_check(PieceColor.BLANCA), "El rey blanco no debería seguir en jaque tras la captura"

    # Promocionar a reina
    promoted = game.promote_pawn(pawn, Queen)
    assert isinstance(promoted, Queen), "Promoción no creó una Queen"
    assert promoted.position == (4, 7), "La pieza promocionada quedó en una casilla incorrecta"

    # Verificar que la nueva Queen sigue reglas normales
    # Intentamos mover verticalmente a una casilla vacía
    can_move = promoted.move(4, 6, game.board)
    assert can_move, "Queen promocionada no puede moverse verticalmente como debería"

    # Intentamos mover a casilla ocupada por pieza amiga (rey)
    can_move = promoted.move(4, 5, game.board)
    assert not can_move, "Queen no debería capturar pieza amiga"

    print("Escenario combinado: promoción bajo jaque – OK")


# -- VALIDACIONES -- #

# Validación tablero – no crear dos piezas en misma casilla.
def test_no_double_placement():
    game = Game()
    game.start_game()

    # Limpiar tablero para controlar situación
    for p in game.board._board[:]:
        game.board.remove_piece(p)

    # Colocar pieza en la casilla (4,4)
    rook1 = Rook(PieceColor.BLANCA, 4, 4)
    game.board.place_piece(rook1, 4, 4)

    # Intentar colocar otra pieza blanca en la misma casilla
    rook2 = Rook(PieceColor.BLANCA, 4, 4)
    try:
        game.board.place_piece(rook2, 4, 4)
        assert False, "No debería permitir colocar dos piezas en la misma casilla"
    except ValueError:
        print("Validación tablero: doble colocación detectada correctamente")

# Validación coordenadas – coordenadas negativas o >7 lanzan error.
def test_invalid_coordinates():
    game = Game()
    game.start_game()

    # Coordenadas negativas
    try:
        game.board.limits(-1, 0)
        assert False, "No debería permitir coordenadas negativas"
    except IndexError:
        print("Coordenada negativa X: OK")

    try:
        game.board.limits(0, -1)
        assert False, "No debería permitir coordenadas negativas"
    except IndexError:
        print("Coordenada negativa Y: OK")

    # Coordenadas mayores a 7
    try:
        game.board.limits(8, 0)
        assert False, "No debería permitir coordenada X > 7"
    except IndexError:
        print("Coordenada X fuera de rango: OK")

    try:
        game.board.limits(0, 8)
        assert False, "No debería permitir coordenada Y > 7"
    except IndexError:
        print("Coordenada Y fuera de rango: OK")

# Movimiento pieza inexistente – falla.
def test_move_nonexistent_piece():
    game = Game()
    game.start_game()

    # Intentar mover pieza donde no hay ninguna
    try:
        game.board.move_piece(4, 4, 4, 5)
        assert False, "No debería permitir mover pieza inexistente"
    except ValueError:
        print("Movimiento de pieza inexistente: OK")

# Bloqueo de piezas – movimiento bloqueado por otra pieza falla.
def test_blocked_piece():
    game = Game()
    game.start_game()

    # Limpiar tablero y colocar torre blanca
    for p in game.board._board[:]:
        game.board.remove_piece(p)

    rook = Rook(PieceColor.BLANCA, 0, 0)
    game.board.place_piece(rook, 0, 0)

    # Colocar peón bloqueando el camino vertical
    pawn = Pawn(PieceColor.BLANCA, 0, 1)
    game.board.place_piece(pawn, 0, 1)

    # Intentar mover torre sobre peón aliado
    can_move = rook.move(0, 2, game.board)
    assert not can_move, "La torre no debería poder moverse sobre pieza bloqueante"
    print("Bloqueo de piezas: OK")

# Captura que deja Rey en jaque – inválida.
def test_capture_leaves_king_in_check():
    game = Game()
    game.start_game()

    # Limpiar tablero
    for p in game.board._board[:]:
        game.board.remove_piece(p)

    # Colocar rey blanco
    king = King(PieceColor.BLANCA, 4, 0)
    game.board.place_piece(king, 4, 0)

    # Colocar torre negra alineada con el rey
    enemy_rook = Rook(PieceColor.NEGRA, 4, 7)
    game.board.place_piece(enemy_rook, 4, 7)

    # Torre blanca protegiendo la columna
    white_rook = Rook(PieceColor.BLANCA, 4, 1)
    game.board.place_piece(white_rook, 4, 1)

    # Pieza enemiga capturable que tentaría a apartar la torre protectora
    enemy_knight = Knight(PieceColor.NEGRA, 5, 1)
    game.board.place_piece(enemy_knight, 5, 1)

    # Capturarla dejaría al rey en jaque, así que debe rechazarse
    moved = game.make_move(white_rook, 5, 1)
    assert not moved, "Una captura que expone al rey al jaque debería fallar"
    print("Captura que deja Rey en jaque: OK")

# Historial consistente – movimiento reflejado en orden correcto tras múltiples movimientos.
def test_movement_history():
    game = Game()
    game.start_game()

    # Mover peón blanco de e2 a e4
    pawn1 = game.board.get_piece(4, 1)
    game.make_move(pawn1, 4, 3)

    # Mover peón negro de d7 a d5
    pawn2 = game.board.get_piece(3, 6)
    game.make_move(pawn2, 3, 4)

    # Mover caballo blanco de g1 a f3
    knight = game.board.get_piece(6, 0)
    game.make_move(knight, 5, 2)

    history = game.movement_history()

    assert history[0]["Piece"] == pawn1 and history[0]["from"] == (4,1) and history[0]["to"] == (4,3)
    assert history[1]["Piece"] == pawn2 and history[1]["from"] == (3,6) and history[1]["to"] == (3,4)
    assert history[2]["Piece"] == knight and history[2]["from"] == (6,0) and history[2]["to"] == (5,2)

    print("Historial consistente: OK")

# Estado juego – get_game_status() devuelve “active”, “checkmate”, “stalemate” o “draw” según situación.
def test_game_status():
    game_controller = GameController()

    # Iniciar partida
    game_controller.start_game()
    status = game_controller.get_game_status()
    assert status == "active", f"Estado debería ser 'active', got {status}"

    # Posición de mate conocida
    for p in game_controller.game.board._board[:]:
        game_controller.game.board.remove_piece(p)

    black_king = King(PieceColor.NEGRA, 0, 0)
    white_queen = Queen(PieceColor.BLANCA, 1, 1)
    white_king = King(PieceColor.BLANCA, 2, 2)
    game_controller.game.board.place_piece(black_king, 0, 0)
    game_controller.game.board.place_piece(white_queen, 1, 1)
    game_controller.game.board.place_piece(white_king, 2, 2)
    game_controller.game.turn = PieceColor.NEGRA

    status = game_controller.get_game_status()
    assert status == "checkmate", f"Estado debería ser 'checkmate', got {status}"

    # Tablas por acuerdo en partida nueva
    game_controller = GameController()
    game_controller.start_game()
    game_controller.game.draw()
    status = game_controller.get_game_status()
    assert status == "draw", f"Estado debería ser 'draw', got {status}"

    print("Estado juego: OK")

# -- INTERACCIONES -- #

# Interacción GameController – make_move() devuelve False si inválido o pieza no existe.
def test_gamecontroller_make_move_invalid():
    gc = GameController()
    gc.start_game()

    # Movimiento inválido: peón blanco intenta moverse diagonal sin captura
    move_invalid = Movement(from_x=0, from_y=1, to_x=1, to_y=2)
    result = gc.make_move(move_invalid)
    assert not result, "make_move debería devolver False para movimiento inválido"

    # Movimiento con pieza inexistente
    move_nonexistent = Movement(from_x=4, from_y=4, to_x=4, to_y=5)
    result2 = gc.make_move(move_nonexistent)
    assert not result2, "make_move debería devolver False para pieza inexistente"

    print("GameController make_move inválido / pieza inexistente: OK")
    
# Interacción GameController – get_board() devuelve tablero correcto.
def test_gamecontroller_get_board():
    gc = GameController()
    board_info = gc.start_game()

    # Comprobar que hay 16 piezas blancas y 16 negras
    white_count = sum(1 for p in board_info if p.color == "BLANCA")
    black_count = sum(1 for p in board_info if p.color == "NEGRA")
    assert white_count == 16, f"Esperadas 16 piezas blancas, got {white_count}"
    assert black_count == 16, f"Esperadas 16 piezas negras, got {black_count}"

    # Comprobar que al menos hay un Rey de cada color
    white_king = any(p.tipo == "King" and p.color == "BLANCA" for p in board_info)
    black_king = any(p.tipo == "King" and p.color == "NEGRA" for p in board_info)
    assert white_king and black_king, "Faltan los reyes en el tablero"

    print("GameController get_board(): OK")
    

# -- SIMULACION DE PARTIDA -- #
 
# Stress test – simular partida completa; verificar reglas y estado final.
def _collect_legal_moves(game: Game):
    legal_moves = []
    for piece in game.board._board:
        if piece.piece_color != game.turn:
            continue
        for x in range(game.board.width):
            for y in range(game.board.height):
                if game._is_legal_move(piece, x, y):
                    legal_moves.append((piece, x, y))
    return legal_moves


def test_full_game_simulation():
    gc = GameController()
    gc.start_game()

    scripted_moves = [
        Movement(from_x=5, from_y=1, to_x=5, to_y=2),  # f2-f3
        Movement(from_x=4, from_y=6, to_x=4, to_y=4),  # e7-e5
        Movement(from_x=6, from_y=1, to_x=6, to_y=3),  # g2-g4
        Movement(from_x=3, from_y=7, to_x=7, to_y=3),  # Dd8-h4 mate
    ]

    for move in scripted_moves:
        moved = gc.make_move(move)
        assert moved, f"La jugada {move} debería ser válida en la simulación completa"

    assert len(gc.game.movement_history()) == 4, "La partida simulada debería registrar 4 movimientos"
    assert gc.get_game_status() == "checkmate", "La partida simulada debería terminar en jaque mate"
    assert not gc.game.active, "La partida debería quedar finalizada tras el jaque mate"

    print("Simulación completa de partida: OK")
 
# Movimiento aleatorio – mover piezas aleatoriamente respeta reglas de turno y captura.
def test_random_move_sequence():
    game = Game()
    game.start_game()
    rng = random.random(42)

    moves_played = 0
    for _ in range(20):
        legal_moves = _collect_legal_moves(game)
        if not legal_moves:
            break

        piece, to_x, to_y = rng.choice(legal_moves)
        moving_color = piece.piece_color
        target_piece = game.board.get_piece(to_x, to_y)
        piece_count_before = len(game.board._board)
        history_len_before = len(game.movement_history())

        assert target_piece is None or target_piece.piece_color != moving_color, "No debería haber capturas propias"

        moved = game.make_move(piece, to_x, to_y)
        assert moved, "Un movimiento aleatorio elegido de la lista legal debería ejecutarse"

        piece_count_after = len(game.board._board)
        history_len_after = len(game.movement_history())
        destination_piece = game.board.get_piece(to_x, to_y)

        assert destination_piece == piece, "La pieza movida debería terminar en la casilla destino"
        assert piece_count_after in (piece_count_before, piece_count_before - 1), "Solo debería cambiar el conteo en capturas"
        assert history_len_after >= history_len_before + 1, "Cada movimiento válido debe registrarse en el historial"
        assert game.turn != moving_color, "El turno debería alternarse tras cada movimiento válido"

        moves_played += 1

    assert moves_played >= 10, f"La secuencia aleatoria debería completar al menos 10 movimientos, got {moves_played}"
    print("Movimiento aleatorio controlado: OK")
 
# Edge case piezas múltiples – mover todas las piezas de un tipo y verificar movimientos válidos.
def test_multiple_same_piece_movements():
    game = Game()
    game.start_game()

    for piece in game.board._board[:]:
        game.board.remove_piece(piece)

    white_king = King(PieceColor.BLANCA, 4, 0)
    black_king = King(PieceColor.NEGRA, 4, 7)
    knights = [
        Knight(PieceColor.BLANCA, 1, 0),
        Knight(PieceColor.BLANCA, 6, 0),
        Knight(PieceColor.NEGRA, 1, 7),
        Knight(PieceColor.NEGRA, 6, 7),
    ]

    game.board.place_piece(white_king, 4, 0)
    game.board.place_piece(black_king, 4, 7)
    for knight in knights:
        game.board.place_piece(knight, knight.x, knight.y)

    move_plan = [
        (knights[0], 2, 2),
        (knights[2], 2, 5),
        (knights[1], 5, 2),
        (knights[3], 5, 5),
    ]

    for piece, to_x, to_y in move_plan:
        moved = game.make_move(piece, to_x, to_y)
        assert moved, f"{piece.__class__.__name__} debería poder moverse a {(to_x, to_y)}"
        assert piece.position == (to_x, to_y), "La pieza debería quedar en la casilla esperada"

    assert len(game.movement_history()) == 4, "Todos los movimientos de las piezas múltiples deben quedar registrados"
    assert game.board.get_piece(2, 2) == knights[0]
    assert game.board.get_piece(2, 5) == knights[2]
    assert game.board.get_piece(5, 2) == knights[1]
    assert game.board.get_piece(5, 5) == knights[3]

    print("Piezas múltiples del mismo tipo: OK")
