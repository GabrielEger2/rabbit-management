from http import HTTPStatus
from fastapi import APIRouter, Query, Path, Depends
from schemas import (
    ExpenseTypesPublic,
    ExpenseTypePublic,
    ExpenseTypeCreate,
    ExpenseTypeUpdate,
)
from common.schemas import Unauthorized
from typing import Optional
from services import ExpenseTypeService, get_expense_type_service

router = APIRouter()


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=ExpenseTypesPublic,
    responses={401: {"model": Unauthorized}},
    summary="Retrieve Expense Types",
    description="Retrieve a list of expense types with pagination and optional sorting.",
)
async def read_expense_types(
    page: Optional[int] = Query(
        1, ge=1, description="Page number, must be greater than or equal to 1"
    ),
    order: Optional[str] = Query(
        None, regex="^(asc|desc)$", description="Order type: [asc, desc]"
    ),
    sort: Optional[str] = Query(
        None, regex="^(name|created_at)$", description="Sort type: [name, created_at]"
    ),
    service: ExpenseTypeService = Depends(get_expense_type_service),
):
    return await service.get_expense_types(page, order, sort)


@router.get(
    "/{type_id}",
    status_code=HTTPStatus.OK,
    response_model=ExpenseTypePublic,
    responses={401: {"model": Unauthorized}},
    summary="Retrieve Expense Type",
    description="Retrieve a single expense type.",
)
async def read_expense_type(
    type_id: str = Path(..., description="ID of the expense type to retrieve"),
    service: ExpenseTypeService = Depends(get_expense_type_service),
):
    return await service.get_expense_type(type_id)


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=ExpenseTypePublic,
    responses={401: {"model": Unauthorized}},
    summary="Create Expense Type",
    description="Creates a new expense type.",
)
async def create_expense_type(
    expense_type_in: ExpenseTypeCreate,
    service: ExpenseTypeService = Depends(get_expense_type_service),
):
    return await service.create_expense_type(expense_type_in.dict())


@router.put(
    "/{type_id}",
    status_code=HTTPStatus.OK,
    response_model=ExpenseTypePublic,
    responses={401: {"model": Unauthorized}},
    summary="Update Expense Type",
    description="Updates an expense type.",
)
async def update_expense_type(
    expense_type_update: ExpenseTypeUpdate,
    type_id: str = Path(..., description="ID of the expense type to update"),
    service: ExpenseTypeService = Depends(get_expense_type_service),
):
    return await service.update_expense_type(type_id, expense_type_update.dict())


@router.delete(
    "/{type_id}",
    status_code=HTTPStatus.NO_CONTENT,
    responses={401: {"model": Unauthorized}},
    summary="Delete Expense Type",
    description="Deletes an expense type.",
)
async def delete_expense_type(
    type_id: str = Path(..., description="ID of the expense type to delete"),
    service: ExpenseTypeService = Depends(get_expense_type_service),
):
    await service.delete_expense_type(type_id)
