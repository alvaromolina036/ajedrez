from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.active_connections: dict[int, dict] = {}

    # Registra un usuario conectado por WebSocket.
    async def connect(self, websocket: WebSocket, user: dict):
        await websocket.accept()
        user_id = int(user["user_id"])
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {
                "user": {
                    "id": user_id,
                    "username": user["username"],
                },
                "websockets": set(),
            }
        self.active_connections[user_id]["websockets"].add(websocket)
        await self.broadcast_presence_changed()

    # Elimina una conexion WebSocket.
    async def disconnect(self, websocket: WebSocket, user_id: int):
        connection = self.active_connections.get(user_id)
        if connection is None:
            return

        connection["websockets"].discard(websocket)
        if not connection["websockets"]:
            self.active_connections.pop(user_id, None)
        await self.broadcast_presence_changed()

    # Lista usuarios conectados.
    def online_users(self) -> list[dict]:
        return [connection["user"] for connection in self.active_connections.values()]

    # Envia un evento a un usuario concreto.
    async def send_to_user(self, user_id: int, message: dict):
        connection = self.active_connections.get(user_id)
        if connection is None:
            return

        for websocket in list(connection["websockets"]):
            await websocket.send_json(message)

    # Envia un evento a todos los clientes conectados.
    async def broadcast(self, message: dict):
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)

    # Avisa de cambios de presencia.
    async def broadcast_presence_changed(self):
        await self.broadcast({
            "type": "presence_changed",
            "users": self.online_users(),
        })

    # Avisa de cambios en una partida.
    async def broadcast_game_updated(self, game_id: int):
        await self.broadcast({
            "type": "game_updated",
            "game_id": game_id,
        })


websocket_manager = WebSocketManager()
