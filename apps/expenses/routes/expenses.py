from http import HTTPStatus
from fastapi import APIRouter, Query, Path, Depends
from schemas import ExpensesPublic, ExpensePublic, ExpenseCreate, ExpenseUpdate
from common.schemas import Unauthorized
from typing import Optional
from services import ExpenseService, get_expense_service

router = APIRouter()


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=ExpensesPublic,
    responses={401: {"model": Unauthorized}},
    summary="Retrieve Expenses",
    description="Retrieve a list of expenses with pagination and optional filtering.",
)
async def read_expenses(
    page: Optional[int] = Query(
        1, ge=1, description="Page number, must be greater than or equal to 1"
    ),
    order: Optional[str] = Query(
        None, regex="^(asc|desc)$", description="Order type: [asc, desc]"
    ),
    sort: Optional[str] = Query(
        None,
        regex="^(amount|incurred_date|created_at)$",
        description="Sort by fields like [amount, incurred_date, created_at]",
    ),
    type_filter: Optional[str] = Query(None, description="Filter by expense type"),
    service: ExpenseService = Depends(get_expense_service),
):
    return await service.get_expenses(page, order, sort, type_filter)


@router.get(
    "/{expense_id}",
    status_code=HTTPStatus.OK,
    response_model=ExpensePublic,
    responses={401: {"model": Unauthorized}},
    summary="Retrieve Expense",
    description="Retrieve a single expense.",
)
async def read_expense(
    expense_id: str = Path(..., description="ID of the expense to retrieve"),
    service: ExpenseService = Depends(get_expense_service),
):
    return await service.get_expense(expense_id)


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=ExpensePublic,
    responses={401: {"model": Unauthorized}},
    summary="Create Expense",
    description="Creates a new expense.",
)
async def create_expense(
    expense_in: ExpenseCreate, service: ExpenseService = Depends(get_expense_service)
):
    return await service.create_expense(expense_in.dict())


@router.put(
    "/{expense_id}",
    status_code=HTTPStatus.OK,
    response_model=ExpensePublic,
    responses={401: {"model": Unauthorized}},
    summary="Update Expense",
    description="Updates an expense.",
)
async def update_expense(
    expense_update: ExpenseUpdate,
    expense_id: str = Path(..., description="ID of the expense to update"),
    service: ExpenseService = Depends(get_expense_service),
):
    return await service.update_expense(expense_id, expense_update.dict())


@router.delete(
    "/{expense_id}",
    status_code=HTTPStatus.NO_CONTENT,
    responses={401: {"model": Unauthorized}},
    summary="Delete Expense",
    description="Deletes an expense.",
)
async def delete_expense(
    expense_id: str = Path(..., description="ID of the expense to delete"),
    service: ExpenseService = Depends(get_expense_service),
):
    await service.delete_expense(expense_id)
