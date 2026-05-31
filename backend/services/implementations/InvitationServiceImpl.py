from backend.adapters.implementations.InvitationAdapterSQL_V2 import InvitationAdapterSQL_V2
from backend.adapters.interfaces.InvitationAdapter import InvitationAdapter
from backend.models.GameModels import GameCreateRequest
from backend.models.InvitationModels import InvitationCreateRequest
from backend.services.implementations.GameServiceImpl import GameServiceImpl
from backend.services.interfaces.InvitationService import InvitationService


class InvitationServiceImpl(InvitationService):
    def __init__(
        self,
        invitation_adapter: InvitationAdapter | None = None,
        game_service: GameServiceImpl | None = None,
    ):
        self.invitation_adapter = invitation_adapter or InvitationAdapterSQL_V2()
        self.game_service = game_service or GameServiceImpl()

    # Envia una invitacion pendiente.
    def send_invitation(self, from_user_id: int, request: InvitationCreateRequest) -> dict:
        if from_user_id == request.to_user_id:
            raise ValueError("No puedes invitarte a ti mismo")
        return self.invitation_adapter.save_invitation(from_user_id, request.to_user_id)

    # Lista invitaciones pendientes recibidas.
    def get_pending_invitations(self, user_id: int) -> list[dict]:
        return self.invitation_adapter.find_pending_for_user(user_id)

    # Acepta una invitacion y crea una partida con la logica existente.
    def accept_invitation(self, invitation_id: int, user_id: int) -> dict | None:
        invitation = self.invitation_adapter.find_by_id(invitation_id)
        if invitation is None:
            return None
        if invitation["to_user_id"] != user_id:
            raise ValueError("La invitacion no pertenece a este usuario")
        if invitation["status"] != "PENDING":
            raise ValueError("La invitacion ya fue respondida")

        updated_invitation = self.invitation_adapter.update_status(invitation_id, "ACCEPTED")
        game = self.game_service.create_game(
            GameCreateRequest(
                white_user_id=invitation["from_user_id"],
                black_user_id=invitation["to_user_id"],
            )
        )
        return {
            "invitation": updated_invitation,
            "game": game,
        }

    # Rechaza una invitacion pendiente.
    def reject_invitation(self, invitation_id: int, user_id: int) -> dict | None:
        invitation = self.invitation_adapter.find_by_id(invitation_id)
        if invitation is None:
            return None
        if invitation["to_user_id"] != user_id:
            raise ValueError("La invitacion no pertenece a este usuario")
        if invitation["status"] != "PENDING":
            raise ValueError("La invitacion ya fue respondida")

        return self.invitation_adapter.update_status(invitation_id, "REJECTED")
