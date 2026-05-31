from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, create_engine, func
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = URL.create(
    "mysql+mysqlconnector",
    username="app_user",
    password="password123",
    host="localhost",
    port=3306,
    database="chess_game",
)

engine = create_engine(DATABASE_URL, connect_args={"use_pure": True})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)


class GameTable(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    white_user_id = Column(Integer, nullable=False)
    black_user_id = Column(Integer, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    board_state = Column(JSON, nullable=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class GameInvitationTable(Base):
    __tablename__ = "game_invitations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_user_id = Column(Integer, nullable=False)
    to_user_id = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
