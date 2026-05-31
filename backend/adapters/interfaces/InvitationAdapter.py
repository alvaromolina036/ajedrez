from abc import ABC, abstractmethod


class InvitationAdapter(ABC):

    # Guarda una invitacion pendiente.
    @abstractmethod
    def save_invitation(self, from_user_id: int, to_user_id: int) -> dict:
        pass

    # Busca una invitacion por id.
    @abstractmethod
    def find_by_id(self, invitation_id: int) -> dict | None:
        pass

    # Lista invitaciones pendientes recibidas por un usuario.
    @abstractmethod
    def find_pending_for_user(self, user_id: int) -> list[dict]:
        pass

    # Actualiza el estado de una invitacion.
    @abstractmethod
    def update_status(self, invitation_id: int, status: str) -> dict | None:
        pass
