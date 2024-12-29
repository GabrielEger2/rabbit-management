from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ExpenseBase(BaseModel):
    type: str
    amount: float
    incurred_date: datetime
    details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)
    observation: Optional[str] = None


class ExpensePublic(ExpenseBase):
    id: str
    created_at: datetime
    updated_at: datetime


class ExpensesPublic(BaseModel):
    data: List[ExpensePublic]
    page: int
    next: Optional[str]


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    type: Optional[str]
    amount: Optional[float]
    incurred_date: Optional[datetime]
    details: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    observation: Optional[str]
