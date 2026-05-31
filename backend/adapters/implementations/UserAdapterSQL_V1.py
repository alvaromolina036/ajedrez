from backend.adapters.implementations.DatabaseConnection import get_connection
from backend.adapters.interfaces.UserAdapter import UserAdapter
from backend.models.UserModels import UserCreateRequest, UserUpdateRequest


class UserAdapterSQL_V1(UserAdapter):

    # Busca un usuario por id usando SQL parametrizado.
    def find_by_id(self, user_id: int) -> dict | None:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username FROM users WHERE id = %s",
            (user_id,),
        )
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user

    # Busca un usuario por username usando SQL parametrizado.
    def find_by_username(self, username: str) -> dict | None:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username FROM users WHERE username = %s",
            (username,),
        )
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user

    # Busca usuarios por id exacto o coincidencia parcial de username.
    def search_users(self, query: str) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        if query.isdigit():
            cursor.execute(
                "SELECT id, username FROM users WHERE id = %s",
                (int(query),),
            )
        else:
            cursor.execute(
                """
                SELECT id, username
                FROM users
                WHERE username LIKE %s
                ORDER BY username
                LIMIT 20
                """,
                (f"%{query}%",),
            )

        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return users

    # Busca id, username y password_hash para autenticacion.
    def find_credentials_by_username(self, username: str) -> dict | None:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            (username,),
        )
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user

    # Guarda un usuario usando SQL parametrizado.
    def save_user(self, request: UserCreateRequest) -> dict:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (request.username, request.password),
        )
        connection.commit()
        user_id = cursor.lastrowid
        cursor.close()
        connection.close()
        return {
            "id": user_id,
            "username": request.username,
        }

    # Actualiza un usuario usando SQL parametrizado.
    def update_user(self, user_id: int, request: UserUpdateRequest) -> dict | None:
        user = self.find_by_id(user_id)
        if user is None:
            return None

        connection = get_connection()
        cursor = connection.cursor()
        if request.password is None:
            new_username = request.username if request.username is not None else user["username"]
            cursor.execute(
                "UPDATE users SET username = %s WHERE id = %s",
                (new_username, user_id),
            )
        else:
            new_username = request.username if request.username is not None else user["username"]
            cursor.execute(
                "UPDATE users SET username = %s, password_hash = %s WHERE id = %s",
                (new_username, request.password, user_id),
            )
        connection.commit()
        cursor.close()
        connection.close()
        return self.find_by_id(user_id)

    # Borra un usuario usando SQL parametrizado.
    def delete_user(self, user_id: int) -> bool:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            DELETE FROM game_invitations
            WHERE from_user_id = %s OR to_user_id = %s
            """,
            (user_id, user_id),
        )
        cursor.execute(
            """
            DELETE FROM games
            WHERE white_user_id = %s OR black_user_id = %s
            """,
            (user_id, user_id),
        )
        cursor.execute(
            "DELETE FROM users WHERE id = %s",
            (user_id,),
        )
        connection.commit()
        deleted = cursor.rowcount > 0
        cursor.close()
        connection.close()
        return deleted
