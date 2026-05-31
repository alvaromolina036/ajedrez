import mysql.connector

# Crea una conexion con la base de datos MariaDB.
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="app_user",
        password="password123",
        database="chess_game",
        use_pure=True,
    )
