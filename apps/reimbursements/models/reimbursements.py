from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import String, Float, Integer
from .base import Base
import datetime


class ReimbursementModel(Base):
    __tablename__ = "reimbursements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    trip_id: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Pending")
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[str] = mapped_column(default=datetime.datetime.now().isoformat())
    updated_at: Mapped[str] = mapped_column(default=datetime.datetime.now().isoformat())

    def __init__(
        self,
        user_id: int,
        trip_id: int,
        status: str,
        total_amount: float,
    ):
        self.user_id = user_id
        self.trip_id = trip_id
        self.status = status
        self.total_amount = total_amount
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = datetime.datetime.now().isoformat()
