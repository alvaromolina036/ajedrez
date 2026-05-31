from backend.engine.tests.tests import *

# -- INICIO PARTIDA NORMAL -- #

# Inicialización del tablero - Crea todas las piezas en sus posiciones correctas.
test_start_game_initial_positions()

# Conteo piezas – 16 Blancas y 16 Negras al iniciar.
test_piece_count_start_game()

# Turno inicial – Comienza con blancas.
test_initial_turn()


# -- MOVIMIENTOS BÁSICOS -- #

# Movimiento básico de Pawn
test_pawn_move()

# Movimiento básico de Knight
test_knight_move()

# Movimiento básico de Bishop
test_bishop_move()

# Movimiento básico de Rook
test_rook_move()

# Movimiento básico de Queen
test_queen_move()

# Movimiento básico de King
test_king_move() 

# Movimiento fuera del tablero – Debe fallar.
test_move_out_of_bounds()


# -- CAPTURAS -- #

# Captura enemiga – Solo se puede capturar piezas del color contrario.
test_capture_enemy()

# Captura propia – Debe fallar.
test_capture_own_piece()

# Captura en_passant – Validar captura de pieza enemiga.
test_en_passant()


# -- MOVIMIENTOS ESPECIALES -- #

# Promoción – Devuelve True cuando Pawn llega a la última fila.
test_can_promote()

# Promoción – Reemplaza peón por pieza válida (Queen, Rook, Bishop, Knight).
test_promote_pawn_valid()

# Promoción inválida – Intentar elegir otro peón o King.
test_promote_pawn_invalid()

# Enroque corto – Validar condiciones.
test_castle_short()

# Enroque largo – Validar condiciones
test_castle_long()

# Enroque bloqueado – Casillas intermedias ocupadas.
test_castle_blocked()

# Enroque con Rey en jaque – Debe fallar. 
test_castle_while_in_check()

# Enroque con pieza ya movida – Debe fallar.
test_castle_piece_moved()


# -- JAQUE / JAQUE MATE / FIN DE PARTIDA -- #
 
# Jaque – Detecta correctamente jaque a King.
test_check_detection()

# Movimiento que deja al King en jaque – Debe rechazarse.
test_move_leaves_king_in_check()

# Jaque mate – checkmate() devuelve True y termina partida.
test_checkmate()

# Ahogado – stalemate() detectado y termina partida.
test_stalemate()

# Tablas por acuerdo – draw() detectado y termina juego.
test_draw()

# Rendición – resign() termina partida y registra jugador.
test_resign()

# -- HISTORIAL DE MOVIMIENTOS -- #
 
# Historial básico – movement_history() registra origen, destino y pieza.
test_movement_history_basic()

# Historial especial – movimientos como enroque, promoción y en_passant registrados correctamente.
test_movement_history_castle()

# -- COMPROBACIÓN MOVIMIENTO DE LAS PIEZAS -- #
 
# Knight – Movimientos en “L” bloqueados por piezas amigas o enemigas.
test_knight_blocked()

# Bishop – No salta sobre piezas.
test_bishop_block()

# Rook – No salta sobre piezas.
test_rook_block()

# Queen – Combina diagonales y rectas con bloqueos respetados.
test_queen_block()

# King – Nunca puede moverse a casilla bajo ataque.
test_king_safe()

# Peones avanzados – No pueden avanzar dos casillas después de mover.
test_pawn_double_move()

# Peones – en_passant solo válido inmediatamente después del avance doble rival.
test_en_passant_timing()

# -- ESCENARIOS COMBINADOS -- #

# Escenarios combinados – jaque + enroque ilegal.
test_check_and_illegal_castle()

# Escenarios combinados – jaque mate con posibilidad de captura de otra pieza - Rey protegido primero.
test_checkmate_with_escape_option()

# Escenarios combinados – promoción en jaque - nueva pieza sigue reglas normales.
test_promotion_under_check()


# -- VALIDACIONES -- #

# Validación tablero – no crear dos piezas en misma casilla.
test_no_double_placement()

# Validación coordenadas – coordenadas negativas o >7 lanzan error.
test_invalid_coordinates()

# Movimiento pieza inexistente – falla.
test_move_nonexistent_piece()

# Bloqueo de piezas – movimiento bloqueado por otra pieza falla.
test_blocked_piece()

# Captura que deja Rey en jaque – inválida.
test_capture_leaves_king_in_check()

# Historial consistente – movimiento reflejado en orden correcto tras múltiples movimientos.
test_movement_history()

# Estado juego – get_game_status() devuelve “active”, “checkmate”, “stalemate” o “draw” según situación.
test_game_status()

# -- INTERACCIONES -- #

# Interacción GameController – make_move() devuelve False si inválido o pieza no existe.
test_gamecontroller_make_move_invalid()

# Interacción GameController – get_board() devuelve tablero correcto.
test_gamecontroller_get_board()

# -- SIMULACION DE PARTIDA --

# Stress test – simular partida completa; verificar reglas y estado final.
 
# Movimiento aleatorio – mover piezas aleatoriamente respeta reglas de turno y captura.
 
# Edge case piezas múltiples – mover todas las piezas de un tipo y verificar movimientos válidos.
