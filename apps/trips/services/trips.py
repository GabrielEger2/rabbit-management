from common.mongo import client
from typing import List, Optional
from datetime import datetime
from schemas import TripsPublic, TripPublic
from common.redis import (
    cache_with_expiry,
    cache_with_sliding_expiry,
    invalidate_cache,
    invalidate_pattern_cache,
)
from fastapi import HTTPException
import re
from bson import ObjectId


class TripService:
    def __init__(self, trips_collection: any):
        self.trips_collection = trips_collection

    async def get_trips(
        self, page: int, order: str, sort: str, name: Optional[str] = None
    ) -> TripsPublic:
        cache_key = f"trips:page={page}:order={order}:sort={sort}:name={name or 'all'}"

        async def fetch_trips():
            query = self._build_trip_query(name)
            sort_order = -1 if order == "desc" else 1
            sort_field = sort if sort in ["name", "created_at"] else "name"

            trips = (
                self.trips_collection.find(query)
                .sort(sort_field, sort_order)
                .skip((page - 1) * 25)
                .limit(26)
                .to_list(26)
            )

            trips_public = [TripPublic(**self._format_trip(trip)) for trip in trips]

            next_page = None
            if len(trips_public) > 25:
                next_page = page + 1
                trips_public = trips_public[:25]

            return {
                "data": [trip.dict() for trip in trips_public],
                "page": page,
                "next": next_page,
            }

        cached_result = await cache_with_expiry(cache_key, fetch_trips, ttl=300)

        return TripsPublic(
            data=[TripPublic(**trip) for trip in cached_result["data"]],
            page=cached_result["page"],
            next=cached_result.get("next"),
        )

    async def get_trip(self, trip_id: str) -> TripPublic:
        if not self._is_valid_object_id(trip_id):
            raise HTTPException(status_code=400, detail="Invalid trip ID format")

        cache_key = f"trip:details:{trip_id}"

        async def fetch_trip():
            trip = self.trips_collection.find_one({"_id": ObjectId(trip_id)})
            if not trip:
                raise HTTPException(
                    status_code=404, detail=f"Trip with ID {trip_id} not found"
                )
            return self._format_trip(trip)

        cached_trip = await cache_with_sliding_expiry(cache_key, fetch_trip, ttl=300)
        return TripPublic(**cached_trip)

    async def create_trip(self, trip: dict) -> TripPublic:
        trip["created_at"] = datetime.utcnow()
        trip["updated_at"] = datetime.utcnow()
        result = self.trips_collection.insert_one(trip)
        trip["_id"] = str(result.inserted_id)

        await invalidate_pattern_cache("trips:*")
        return TripPublic(**self._format_trip(trip))

    async def update_trip(self, trip_id: str, trip_update: dict) -> TripPublic:
        if not self._is_valid_object_id(trip_id):
            raise HTTPException(status_code=400, detail="Invalid trip ID format")

        trip_update["updated_at"] = datetime.utcnow()
        update_result = self.trips_collection.update_one(
            {"_id": ObjectId(trip_id)}, {"$set": trip_update}
        )

        if update_result.matched_count == 0:
            raise HTTPException(
                status_code=404, detail=f"Trip with ID {trip_id} not found"
            )

        updated_trip = self.trips_collection.find_one({"_id": trip_id})
        await invalidate_cache(f"trip:details:{trip_id}")
        await invalidate_pattern_cache("trips:*")
        return TripPublic(**self._format_trip(updated_trip))

    async def delete_trip(self, trip_id: str) -> None:
        if not self._is_valid_object_id(trip_id):
            raise HTTPException(status_code=400, detail="Invalid trip ID format")

        delete_result = self.trips_collection.delete_one({"_id": ObjectId(trip_id)})
        if delete_result.deleted_count == 0:
            raise HTTPException(
                status_code=404, detail=f"Trip with ID {trip_id} not found"
            )

        await invalidate_cache(f"trip:details:{trip_id}")
        await invalidate_pattern_cache("trips:*")

    def _build_trip_query(self, name: Optional[str]) -> dict:
        query = {}
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        return query

    def _format_trip(self, trip: dict) -> dict:
        if trip is None:
            return {}
        trip["id"] = str(trip["_id"])  # Convert ObjectId to string
        trip.pop("_id", None)  # Optionally remove the original _id field
        trip["created_at"] = (
            trip.get("created_at").isoformat() if "created_at" in trip else None
        )
        trip["updated_at"] = (
            trip.get("updated_at").isoformat() if "updated_at" in trip else None
        )
        return trip

    @staticmethod
    def _is_valid_object_id(object_id: str) -> bool:
        return bool(re.match(r"^[a-fA-F0-9]{24}$", object_id))

    @staticmethod
    def _get_collection():
        db = client.trips_db
        return db["trips"]


def get_trip_service() -> TripService:
    return TripService(TripService._get_collection())
