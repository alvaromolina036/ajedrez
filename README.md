# Ajedrez academico

Proyecto web de ajedrez orientado a auditoria academica. Mantiene una arquitectura por capas con autenticacion JWT, usuarios, partidas, motor de ajedrez, persistencia en MariaDB y adapters con implementacion SQL directa y ORM.

## Funcionalidades mantenidas

- Registro, login y verificacion de sesion con JWT.
- Busqueda, consulta, actualizacion y borrado de usuarios.
- Creacion, listado, consulta y borrado de partidas.
- Carga del tablero y estado completo de una partida.
- Ejecucion de movimientos mediante el motor de ajedrez.
- Persistencia del estado del tablero en MariaDB.
- Frontend minimo para login, panel de partidas y tablero.

## Tecnologias

### Backend

- Python
- FastAPI
- Uvicorn
- MariaDB
- mysql-connector-python
- SQLAlchemy
- JWT

### Frontend

- HTML5
- CSS3
- JavaScript
- Consumo de API REST con `fetch`

## Arquitectura

El backend sigue una separacion por capas:

- `controllers`: endpoints REST.
- `services`: reglas de aplicacion.
- `adapters`: acceso a datos mediante interfaces.
- `models`: modelos de entrada y salida.
- `engine`: logica de ajedrez.
- `utils`: seguridad, JWT y dependencias de autenticacion.

La persistencia conserva dos estilos de acceso:

- SQL directo: `GameAdapterSQL_V1` y `UserAdapterSQL_V1`.
- ORM: `GameAdapterSQL_V2` y `UserAdapterSQL_V2`.

`FileAdapter` se mantiene como adapter de fichero para cumplir la separacion de infraestructura.

## Endpoints principales

- `GET /`: estado del servidor.
- `POST /users`: registrar usuario.
- `GET /users/search?query=...`: buscar usuarios.
- `GET /users/{user_id}`: consultar usuario por id.
- `PUT /users/{user_id}`: actualizar usuario.
- `DELETE /users/{user_id}`: borrar usuario.
- `POST /authentication/login`: iniciar sesion.
- `GET /authentication/verify`: verificar JWT.
- `GET /games`: listar partidas activas guardadas.
- `POST /games`: crear partida.
- `GET /games/{game_id}`: consultar partida.
- `GET /games/{game_id}/board`: consultar tablero.
- `GET /games/{game_id}/state`: consultar partida, tablero y turno.
- `PUT /games/{game_id}/move`: realizar movimiento.
- `DELETE /games/{game_id}`: borrar partida.

## Flujo de uso

1. El usuario se registra o inicia sesion.
2. El frontend guarda el JWT en `sessionStorage`.
3. El usuario busca un rival por nombre o id.
4. Se crea una partida mediante `POST /games`.
5. El tablero se carga con `GET /games/{id}/state`.
6. Cada movimiento se envia con `PUT /games/{id}/move`.
7. El estado actualizado se persiste en MariaDB.

## Validacion

Con el backend activo, ejecutar:

```bash
python test.py
```

La validacion comprueba autenticacion, usuarios, busqueda, creacion/listado de partidas, estado del tablero, movimientos y persistencia en `games.board_state`.
