from typing import List, Optional
from sqlmodel import SQLModel, Field
import datetime
from pydantic import BaseModel


class ReimbursementBase(SQLModel):
    user_id: int = Field(index=True)
    trip_id: Optional[int] = None
    status: str = Field(default="Pending")
    total_amount: float = Field(default=0.0)


class ReimbursementPublic(ReimbursementBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ReimbursementsPublic(SQLModel):
    data: List[ReimbursementPublic]
    page: int
    next: Optional[str]


class ReimbursementCreate(ReimbursementBase):
    expense_ids: List[int]


class ReimbursementUpdate(SQLModel):
    trip_id: Optional[int]
    status: Optional[str]
    expense_ids: Optional[List[int]]
    total_amount: Optional[float]

class ReimbursementCreatePublic(BaseModel):
    message: str
