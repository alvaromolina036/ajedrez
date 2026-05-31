from fastapi import APIRouter, Depends, HTTPException

from backend.models.InvitationModels import InvitationCreateRequest
from backend.services.implementations.InvitationServiceImpl import InvitationServiceImpl
from backend.utils.AuthDependencies import require_authenticated_user
from backend.utils.WebSocketManager import websocket_manager

router = APIRouter(prefix="/invitations", tags=["invitations"])
invitation_service = InvitationServiceImpl()


# Envia una invitacion a otro usuario.
@router.post("")
async def send_invitation(
    request: InvitationCreateRequest,
    authenticated_user: dict = Depends(require_authenticated_user),
):
    if request.to_user_id <= 0:
        raise HTTPException(status_code=400, detail="to_user_id debe ser mayor que 0")

    try:
        invitation = invitation_service.send_invitation(
            int(authenticated_user["user_id"]),
            request,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    await websocket_manager.send_to_user(request.to_user_id, {
        "type": "invitation_received",
        "invitation_id": invitation["id"],
    })
    return invitation


# Lista invitaciones pendientes del usuario autenticado.
@router.get("/pending")
def get_pending_invitations(authenticated_user: dict = Depends(require_authenticated_user)):
    return invitation_service.get_pending_invitations(int(authenticated_user["user_id"]))


# Acepta una invitacion pendiente y crea una partida.
@router.put("/{invitation_id}/accept")
async def accept_invitation(
    invitation_id: int,
    authenticated_user: dict = Depends(require_authenticated_user),
):
    if invitation_id <= 0:
        raise HTTPException(status_code=400, detail="invitation_id debe ser mayor que 0")

    try:
        result = invitation_service.accept_invitation(
            invitation_id,
            int(authenticated_user["user_id"]),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if result is None:
        raise HTTPException(status_code=404, detail="Invitacion no encontrada")

    invitation = result["invitation"]
    game = result["game"]
    await websocket_manager.send_to_user(invitation["from_user_id"], {
        "type": "invitation_answered",
        "invitation_id": invitation_id,
        "status": "ACCEPTED",
        "game_id": game["id"],
    })
    await websocket_manager.broadcast_game_updated(game["id"])
    return result


# Rechaza una invitacion pendiente.
@router.put("/{invitation_id}/reject")
async def reject_invitation(
    invitation_id: int,
    authenticated_user: dict = Depends(require_authenticated_user),
):
    if invitation_id <= 0:
        raise HTTPException(status_code=400, detail="invitation_id debe ser mayor que 0")

    try:
        invitation = invitation_service.reject_invitation(
            invitation_id,
            int(authenticated_user["user_id"]),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitacion no encontrada")

    await websocket_manager.send_to_user(invitation["from_user_id"], {
        "type": "invitation_answered",
        "invitation_id": invitation_id,
        "status": "REJECTED",
    })
    return invitation
