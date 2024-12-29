from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ExpenseTypeBase(BaseModel):
    name: str
    description: str
    max_reimbursement: float
    creator: str
    observations: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ExpenseTypePublic(ExpenseTypeBase):
    id: str
    created_at: datetime
    updated_at: datetime


class ExpenseTypesPublic(BaseModel):
    data: List[ExpenseTypePublic]
    page: int
    next: Optional[str]


class ExpenseTypeCreate(ExpenseTypeBase):
    pass


class ExpenseTypeUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    max_reimbursement: Optional[float]
    observations: Optional[Dict[str, Any]]
