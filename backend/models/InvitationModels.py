from pydantic import BaseModel


# Datos necesarios para enviar una invitacion.
class InvitationCreateRequest(BaseModel):
    to_user_id: int
