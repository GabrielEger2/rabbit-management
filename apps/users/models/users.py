from sqlalchemy.orm import Mapped, mapped_column
import datetime
from .base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    level: Mapped[int] = mapped_column(default=1)
    joined: Mapped[str] = mapped_column(default=datetime.datetime.now().isoformat())

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        is_active: bool = True,
        level: int = 1,
    ):
        self.username = username
        self.email = email
        self.password = password
        self.is_active = is_active
        self.level = level
        self.joined = datetime.datetime.now().isoformat()
