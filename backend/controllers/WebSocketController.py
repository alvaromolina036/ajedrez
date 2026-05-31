from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.utils.SecurityUtils import verify_jwt
from backend.utils.WebSocketManager import websocket_manager

router = APIRouter(tags=["websocket"])


# Mantiene una conexion WebSocket autenticada para avisos en tiempo real.
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user = verify_jwt(token)
    if user is None:
        await websocket.close(code=1008)
        return

    user_id = int(user["user_id"])
    await websocket_manager.connect(websocket, user)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, user_id)
