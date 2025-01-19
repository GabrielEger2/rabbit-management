from http import HTTPStatus
from fastapi import APIRouter, Path, Query, Depends
from schemas import (
    ReimbursementsPublic,
    ReimbursementPublic,
    ReimbursementCreate,
    ReimbursementUpdate,
    ReimbursementCreatePublic
)
from common.schemas import Unauthorized
from typing import Optional
from services import ReimbursementService, get_reimbursement_service

router = APIRouter()


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=ReimbursementsPublic,
    responses={401: {"model": Unauthorized}},
    summary="Retrieve Reimbursements",
    description="Retrieve a list of reimbursements with pagination and optional filtering.",
)
async def read_reimbursements(
    page: Optional[int] = Query(
        1, ge=1, description="Page number, must be greater than or equal to 1"
    ),
    status: Optional[str] = Query(
        None, description="Filter by reimbursement status (Pending, Approved, Rejected)"
    ),
    service: ReimbursementService = Depends(get_reimbursement_service),
):
    return await service.get_reimbursements(page, status)


@router.get(
    "/{reimbursement_id}",
    status_code=HTTPStatus.OK,
    response_model=ReimbursementPublic,
    responses={401: {"model": Unauthorized}},
    summary="Retrieve Reimbursement",
    description="Retrieve a single reimbursement.",
)
async def read_reimbursement(
    reimbursement_id: int = Path(
        ..., description="ID of the reimbursement to retrieve"
    ),
    service: ReimbursementService = Depends(get_reimbursement_service),
):
    return await service.get_reimbursement(reimbursement_id)


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=ReimbursementCreatePublic,
    responses={401: {"model": Unauthorized}},
    summary="Create Reimbursement",
    description="Creates a new reimbursement request.",
)
async def create_reimbursement(
    reimbursement_in: ReimbursementCreate,
    service: ReimbursementService = Depends(get_reimbursement_service),
):
    return await service.create_reimbursement(reimbursement_in)


@router.put(
    "/{reimbursement_id}",
    status_code=HTTPStatus.OK,
    response_model=ReimbursementPublic,
    responses={401: {"model": Unauthorized}},
    summary="Update Reimbursement",
    description="Updates a reimbursement.",
)
async def update_reimbursement(
    reimbursement_update: ReimbursementUpdate,
    reimbursement_id: int = Path(..., description="ID of the reimbursement to update"),
    service: ReimbursementService = Depends(get_reimbursement_service),
):
    return await service.update_reimbursement(reimbursement_id, reimbursement_update)

    return await service.update_reimbursement(reimbursement_id, reimbursement_update)