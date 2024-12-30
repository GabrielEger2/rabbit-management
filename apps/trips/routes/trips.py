from http import HTTPStatus
from fastapi import APIRouter, Query, Path, Depends
from schemas import TripsPublic, TripPublic, TripCreate, TripUpdate
from common.schemas import Unauthorized
from typing import Optional
from services import TripService, get_trip_service

router = APIRouter()


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=TripsPublic,
    responses={401: {"model": Unauthorized}},
    summary="Retrieve Trips",
    description="Retrieve a list of trips with pagination and optional sorting.",
)
async def read_trips(
    page: Optional[int] = Query(
        1,
        ge=1,
        description="Page number, must be greater than or equal to 1",
    ),
    order: Optional[str] = Query(
        None,
        regex="^(asc|desc)$",
        description="Order type: [asc, desc], default is ascending",
    ),
    sort: Optional[str] = Query(
        None,
        regex="^(name|created_at)$",
        description="Sort type: [name, created_at], default is name",
    ),
    name: Optional[str] = Query(None, description="Filter by trip name"),
    service: TripService = Depends(get_trip_service),
):
    return await service.get_trips(page, order, sort, name)


@router.get(
    "/{trip_id}",
    status_code=HTTPStatus.OK,
    response_model=TripPublic,
    responses={401: {"model": Unauthorized}},
    summary="Retrieve Trip",
    description="Retrieve a single trip.",
)
async def read_trip(
    trip_id: str = Path(..., description="ID of the trip to retrieve"),
    service: TripService = Depends(get_trip_service),
):
    return await service.get_trip(trip_id)


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=TripPublic,
    responses={401: {"model": Unauthorized}},
    summary="Create Trip",
    description="Creates a new trip.",
)
async def create_trip(
    trip_in: TripCreate, service: TripService = Depends(get_trip_service)
):
    return await service.create_trip(trip_in.dict())


@router.put(
    "/{trip_id}",
    status_code=HTTPStatus.OK,
    response_model=TripPublic,
    responses={401: {"model": Unauthorized}},
    summary="Update Trip",
    description="Updates a trip.",
)
async def update_trip(
    trip_update: TripUpdate,
    trip_id: str = Path(..., description="ID of the trip to update"),
    service: TripService = Depends(get_trip_service),
):
    return await service.update_trip(trip_id, trip_update.dict())


@router.delete(
    "/{trip_id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Delete Trip",
    responses={401: {"model": Unauthorized}},
    description="Deletes a trip.",
)
async def delete_trip(
    trip_id: str = Path(..., description="ID of the trip to delete"),
    service: TripService = Depends(get_trip_service),
):
    await service.delete_trip(trip_id)
