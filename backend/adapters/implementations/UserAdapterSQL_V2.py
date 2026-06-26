from backend.adapters.implementations.ORMConnection import GameTable, SessionLocal, UserTable
from backend.adapters.interfaces.UserAdapter import UserAdapter
from backend.models.UserModels import UserCreateRequest, UserUpdateRequest


class UserAdapterSQL_V2(UserAdapter):

    # Convierte un usuario ORM en diccionario.
    def _to_dict(self, user: UserTable) -> dict:
        return {
            "id": user.id,
            "username": user.username,
        }

    # Busca un usuario por id usando ORM.
    def find_by_id(self, user_id: int) -> dict | None:
        with SessionLocal() as session:
            user = session.get(UserTable, user_id)
            if user is None:
                return None
            return self._to_dict(user)

    # Busca un usuario por username usando ORM.
    def find_by_username(self, username: str) -> dict | None:
        with SessionLocal() as session:
            user = session.query(UserTable).filter(UserTable.username == username).first()
            if user is None:
                return None
            return self._to_dict(user)

    # Busca usuarios por id exacto o coincidencia parcial de username.
    def search_users(self, query: str) -> list[dict]:
        with SessionLocal() as session:
            if query.isdigit():
                user = session.get(UserTable, int(query))
                return [] if user is None else [self._to_dict(user)]

            users = (
                session.query(UserTable)
                .filter(UserTable.username.like(f"%{query}%"))
                .order_by(UserTable.username)
                .limit(20)
                .all()
            )
            return [self._to_dict(user) for user in users]

    # Busca id, username y password_hash para autenticacion.
    def find_credentials_by_username(self, username: str) -> dict | None:
        with SessionLocal() as session:
            user = session.query(UserTable).filter(UserTable.username == username).first()
            if user is None:
                return None
            return {
                "id": user.id,
                "username": user.username,
                "password_hash": user.password_hash,
            }

    # Guarda un usuario usando ORM.
    def save_user(self, request: UserCreateRequest) -> dict:
        with SessionLocal() as session:
            user = UserTable(
                username=request.username,
                password_hash=request.password,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return self._to_dict(user)

    # Actualiza un usuario usando ORM.
    def update_user(self, user_id: int, request: UserUpdateRequest) -> dict | None:
        with SessionLocal() as session:
            user = session.get(UserTable, user_id)
            if user is None:
                return None

            if request.username is not None:
                user.username = request.username
            if request.password is not None:
                user.password_hash = request.password

            session.commit()
            session.refresh(user)
            return self._to_dict(user)

    # Borra un usuario usando ORM.
    def delete_user(self, user_id: int) -> bool:
        with SessionLocal() as session:
            user = session.get(UserTable, user_id)
            if user is None:
                return False

            session.query(GameTable).filter(
                (GameTable.white_user_id == user_id) |
                (GameTable.black_user_id == user_id)
            ).delete(synchronize_session=False)
            session.delete(user)
            session.commit()
            return True
