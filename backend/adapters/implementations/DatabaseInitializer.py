from backend.adapters.implementations.DatabaseConnection import get_connection


# Crea o actualiza las tablas necesarias sin romper datos existentes.
def ensure_database_schema():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS games (
            id INT AUTO_INCREMENT PRIMARY KEY,
            white_user_id INT NOT NULL,
            black_user_id INT NOT NULL,
            active BOOLEAN NOT NULL DEFAULT TRUE
        )
        """
    )

    cursor.execute("SHOW COLUMNS FROM games LIKE 'board_state'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE games ADD COLUMN board_state JSON NULL")

    cursor.execute("SHOW COLUMNS FROM games LIKE 'updated_at'")
    if cursor.fetchone() is None:
        cursor.execute(
            """
            ALTER TABLE games
            ADD COLUMN updated_at DATETIME NOT NULL
            DEFAULT CURRENT_TIMESTAMP
            ON UPDATE CURRENT_TIMESTAMP
            """
        )

    connection.commit()
    cursor.close()
    connection.close()
