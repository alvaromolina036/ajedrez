from backend.adapters.implementations.ORMConnection import GameInvitationTable, SessionLocal
from backend.adapters.interfaces.InvitationAdapter import InvitationAdapter


class InvitationAdapterSQL_V2(InvitationAdapter):

    # Convierte una invitacion ORM en diccionario.
    def _to_dict(self, invitation: GameInvitationTable) -> dict:
        return {
            "id": invitation.id,
            "from_user_id": invitation.from_user_id,
            "to_user_id": invitation.to_user_id,
            "status": invitation.status,
            "created_at": invitation.created_at.isoformat() if invitation.created_at is not None else None,
        }

    # Guarda una invitacion pendiente usando ORM.
    def save_invitation(self, from_user_id: int, to_user_id: int) -> dict:
        with SessionLocal() as session:
            invitation = GameInvitationTable(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                status="PENDING",
            )
            session.add(invitation)
            session.commit()
            session.refresh(invitation)
            return self._to_dict(invitation)

    # Busca una invitacion por id usando ORM.
    def find_by_id(self, invitation_id: int) -> dict | None:
        with SessionLocal() as session:
            invitation = session.get(GameInvitationTable, invitation_id)
            if invitation is None:
                return None
            return self._to_dict(invitation)

    # Lista invitaciones pendientes recibidas por un usuario usando ORM.
    def find_pending_for_user(self, user_id: int) -> list[dict]:
        with SessionLocal() as session:
            invitations = (
                session.query(GameInvitationTable)
                .filter(
                    GameInvitationTable.to_user_id == user_id,
                    GameInvitationTable.status == "PENDING",
                )
                .order_by(GameInvitationTable.created_at.desc())
                .all()
            )
            return [self._to_dict(invitation) for invitation in invitations]

    # Actualiza el estado de una invitacion usando ORM.
    def update_status(self, invitation_id: int, status: str) -> dict | None:
        with SessionLocal() as session:
            invitation = session.get(GameInvitationTable, invitation_id)
            if invitation is None:
                return None

            invitation.status = status
            session.commit()
            session.refresh(invitation)
            return self._to_dict(invitation)
