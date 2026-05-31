from abc import ABC, abstractmethod

from backend.models.InvitationModels import InvitationCreateRequest


class InvitationService(ABC):

    # Envia una invitacion a otro usuario.
    @abstractmethod
    def send_invitation(self, from_user_id: int, request: InvitationCreateRequest) -> dict:
        pass

    # Lista invitaciones pendientes de un usuario.
    @abstractmethod
    def get_pending_invitations(self, user_id: int) -> list[dict]:
        pass

    # Acepta una invitacion y crea una partida.
    @abstractmethod
    def accept_invitation(self, invitation_id: int, user_id: int) -> dict | None:
        pass

    # Rechaza una invitacion.
    @abstractmethod
    def reject_invitation(self, invitation_id: int, user_id: int) -> dict | None:
        pass
