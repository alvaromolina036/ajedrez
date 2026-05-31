import asyncio
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

try:
    import requests  # type: ignore
except ImportError:
    requests = None

try:
    import websockets
except ImportError:
    websockets = None


API_CANDIDATES = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
]


@dataclass
class ApiResponse:
    status_code: int
    data: Any


class ApiError(Exception):
    def __init__(self, status_code: int, data: Any):
        self.status_code = status_code
        self.data = data
        super().__init__(f"HTTP {status_code}: {data}")


class ApiClient:
    def __init__(self):
        self.base_url = self._resolve_base_url()

    def _resolve_base_url(self) -> str:
        for base_url in API_CANDIDATES:
            try:
                response = self.request("GET", "/", base_url=base_url, allow_error=True)
                if response.status_code == 200 and response.data.get("mensaje") == "Servidor activo":
                    return base_url
            except Exception:
                pass
        raise RuntimeError("No se ha encontrado el backend activo en 127.0.0.1:8000 ni 127.0.0.1:8001")

    def request(
        self,
        method: str,
        path: str,
        body: dict | None = None,
        token: str | None = None,
        base_url: str | None = None,
        allow_error: bool = False,
    ) -> ApiResponse:
        url = f"{base_url or self.base_url}{path}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"

        if requests is not None:
            response = requests.request(method, url, headers=headers, json=body, timeout=8)
            try:
                data = response.json()
            except ValueError:
                data = None
            if response.status_code >= 400 and not allow_error:
                raise ApiError(response.status_code, data)
            return ApiResponse(response.status_code, data)

        payload = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(url, data=payload, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw) if raw else None
                return ApiResponse(response.status, data)
        except urllib.error.HTTPError as error:
            raw = error.read().decode("utf-8")
            data = json.loads(raw) if raw else None
            if not allow_error:
                raise ApiError(error.code, data)
            return ApiResponse(error.code, data)


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def check(self, name: str, condition: bool, detail: str = ""):
        if condition:
            self.passed += 1
            print(f"PASS - {name}")
        else:
            self.failed += 1
            print(f"FAIL - {name}{': ' + detail if detail else ''}")

    def fail(self, name: str, error: Exception):
        self.failed += 1
        print(f"FAIL - {name}: {error}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\nRESULTADO: {self.passed}/{total} tests PASS")
        if self.failed:
            raise SystemExit(1)


def find_piece(board: list[dict], x: int, y: int) -> dict | None:
    return next((piece for piece in board if piece.get("x") == x and piece.get("y") == y), None)


def read_board_state_from_database(game_id: int) -> dict | None:
    try:
        import mysql.connector
    except ImportError:
        return None

    connection = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="app_user",
        password="password123",
        database="chess_game",
        use_pure=True,
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT board_state FROM games WHERE id = %s", (game_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if row is None or row["board_state"] is None:
        return None
    if isinstance(row["board_state"], dict):
        return row["board_state"]
    return json.loads(row["board_state"])


async def wait_for_event(websocket, event_type: str, timeout: int = 6) -> dict:
    end_time = time.time() + timeout
    while time.time() < end_time:
        remaining = max(0.1, end_time - time.time())
        message = await asyncio.wait_for(websocket.recv(), timeout=remaining)
        data = json.loads(message)
        if data.get("type") == event_type:
            return data
    raise TimeoutError(f"No se recibio evento {event_type}")


async def run_websocket_test(
    runner: TestRunner,
    api: ApiClient,
    token_a: str,
    token_b: str,
    game_id: int,
):
    if websockets is None:
        runner.check("WebSocket disponible", False, "No esta instalado el paquete websockets")
        return

    ws_base_url = api.base_url.replace("http://", "ws://").replace("https://", "wss://")
    url_a = f"{ws_base_url}/ws?token={token_a}"
    url_b = f"{ws_base_url}/ws?token={token_b}"

    async with websockets.connect(url_a) as ws_a, websockets.connect(url_b) as ws_b:
        online = api.request("GET", "/users/online", token=token_a).data
        runner.check("GET /users/online", len(online) >= 2)

        api.request(
            "PUT",
            f"/games/{game_id}/move",
            {"from_x": 0, "from_y": 6, "to_x": 0, "to_y": 5},
            token=token_b,
        )

        event = await wait_for_event(ws_a, "game_updated")
        runner.check("WebSocket recibe game_updated", event.get("game_id") == game_id)

        refreshed_state = api.request("GET", f"/games/{game_id}/state", token=token_a).data
        runner.check("Segundo cliente refresca estado sin recargar", refreshed_state["turn"] == "BLANCA")


def main():
    runner = TestRunner()
    api = ApiClient()
    created_users: list[tuple[int, str | None]] = []
    created_games: list[tuple[int, str | None]] = []

    print(f"Backend detectado: {api.base_url}")
    if requests is None:
        print("INFO - requests/httpx no estan instalados; se usa urllib como fallback HTTP.")

    suffix = str(int(time.time()))
    user_a = {"username": f"qa_a_{suffix}", "password": "test1234"}
    user_b = {"username": f"qa_b_{suffix}", "password": "test1234"}
    user_c = {"username": f"qa_c_{suffix}", "password": "test1234"}

    token_a = None
    token_b = None
    token_c = None
    direct_game_id = None

    try:
        created_a = api.request("POST", "/users", user_a).data
        created_b = api.request("POST", "/users", user_b).data
        created_c = api.request("POST", "/users", user_c).data
        runner.check("Registro de usuario", all(user.get("id") for user in [created_a, created_b, created_c]))

        login_a = api.request("POST", "/authentication/login", user_a).data
        login_b = api.request("POST", "/authentication/login", user_b).data
        login_c = api.request("POST", "/authentication/login", user_c).data
        token_a = login_a["token"]
        token_b = login_b["token"]
        token_c = login_c["token"]
        created_users.extend([
            (created_a["id"], token_a),
            (created_b["id"], token_a),
            (created_c["id"], token_a),
        ])
        runner.check("Login con JWT valido", bool(token_a and token_b and token_c))

        bad_login = api.request(
            "POST",
            "/authentication/login",
            {"username": user_a["username"], "password": "password_mal"},
            allow_error=True,
        )
        runner.check("Login con credenciales incorrectas", bad_login.status_code == 401)

        search_by_username = api.request("GET", f"/users/search?query={user_b['username']}", token=token_a).data
        runner.check("GET /users/search?query= por username", search_by_username[0]["id"] == created_b["id"])

        search_by_id = api.request("GET", f"/users/search?query={created_b['id']}", token=token_a).data
        runner.check("GET /users/search?query= por ID", search_by_id[0]["username"] == user_b["username"])

        direct_game = api.request(
            "POST",
            "/games",
            {"white_user_id": created_a["id"], "black_user_id": created_b["id"]},
            token=token_a,
        ).data
        direct_game_id = direct_game["id"]
        created_games.append((direct_game_id, token_a))
        runner.check("POST /games crea partida", direct_game["active"] is True)

        live_games = api.request("GET", "/games/live", token=token_a).data
        runner.check("GET /games/live", any(game["id"] == direct_game_id for game in live_games))

        state_before = api.request("GET", f"/games/{direct_game_id}/state", token=token_a).data
        runner.check("GET /games/{id}/state", len(state_before["board"]) == 32 and state_before["turn"] == "BLANCA")

        board_before = api.request("GET", f"/games/{direct_game_id}/board", token=token_a).data
        runner.check("GET /games/{id}/board", len(board_before) == 32)

        api.request(
            "PUT",
            f"/games/{direct_game_id}/move",
            {"from_x": 0, "from_y": 1, "to_x": 0, "to_y": 2},
            token=token_a,
        )
        state_after = api.request("GET", f"/games/{direct_game_id}/state", token=token_a).data
        runner.check(
            "PUT /games/{id}/move cambia estado",
            find_piece(state_after["board"], 0, 1) is None and find_piece(state_after["board"], 0, 2) is not None,
        )
        runner.check("Turno cambia despues del movimiento", state_after["turn"] == "NEGRA")

        board_state = read_board_state_from_database(direct_game_id)
        runner.check(
            "Persistencia en games.board_state",
            board_state is not None
            and board_state.get("turn") == "NEGRA"
            and find_piece(board_state.get("board", []), 0, 2) is not None,
        )

        reject_invitation = api.request(
            "POST",
            "/invitations",
            {"to_user_id": created_c["id"]},
            token=token_a,
        ).data
        pending_c = api.request("GET", "/invitations/pending", token=token_c).data
        runner.check("POST /invitations y GET /invitations/pending", any(inv["id"] == reject_invitation["id"] for inv in pending_c))

        rejected = api.request("PUT", f"/invitations/{reject_invitation['id']}/reject", token=token_c).data
        runner.check("PUT /invitations/{id}/reject", rejected["status"] == "REJECTED")

        accept_invitation = api.request(
            "POST",
            "/invitations",
            {"to_user_id": created_b["id"]},
            token=token_a,
        ).data
        accepted = api.request("PUT", f"/invitations/{accept_invitation['id']}/accept", token=token_b).data
        created_games.append((accepted["game"]["id"], token_a))
        runner.check(
            "PUT /invitations/{id}/accept",
            accepted["invitation"]["status"] == "ACCEPTED" and accepted["game"]["active"] is True,
        )

        asyncio.run(run_websocket_test(runner, api, token_a, token_b, direct_game_id))

    except Exception as error:
        runner.fail("Ejecucion general de tests", error)

    finally:
        for game_id, token in created_games:
            if token is None:
                continue
            try:
                api.request("DELETE", f"/games/{game_id}", token=token, allow_error=True)
            except Exception:
                pass

        for user_id, token in created_users:
            if token is None:
                continue
            try:
                api.request("DELETE", f"/users/{user_id}", token=token, allow_error=True)
            except Exception:
                pass

    runner.summary()


if __name__ == "__main__":
    main()
