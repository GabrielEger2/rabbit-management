from common.mongo import client
from typing import List, Optional
from datetime import datetime
from schemas import ExpenseTypesPublic, ExpenseTypePublic
from common.redis import (
    cache_with_expiry,
    cache_with_sliding_expiry,
    invalidate_cache,
    invalidate_pattern_cache,
)
from fastapi import HTTPException
import re
from bson import ObjectId

class ExpenseTypeService:
    def __init__(self, expense_types_collection: any):
        self.expense_types_collection = expense_types_collection

    async def get_expense_types(self, page: int, order: str, sort: str) -> ExpenseTypesPublic:
        cache_key = f"expense_types:page={page}:order={order}:sort={sort}"

        async def fetch_expense_types():
            sort_order = -1 if order == "desc" else 1
            sort_field = sort if sort in ["name", "created_at"] else "name"

            expense_types = (
                self.expense_types_collection.find({})
                .sort(sort_field, sort_order)
                .skip((page - 1) * 25)
                .limit(26)
                .to_list(26)
            )

            expense_types_public = [ExpenseTypePublic(**self._format_expense_type(exp)) for exp in expense_types]

            next_page = None
            if len(expense_types_public) > 25:
                next_page = page + 1
                expense_types_public = expense_types_public[:25]

            return {
                "data": [expense_type.dict() for expense_type in expense_types_public],
                "page": page,
                "next": next_page,
            }

        cached_result = await cache_with_expiry(cache_key, fetch_expense_types, ttl=300)

        return ExpenseTypesPublic(
            data=[ExpenseTypePublic(**expense_type) for expense_type in cached_result["data"]],
            page=cached_result["page"],
            next=cached_result.get("next"),
        )

    async def get_expense_type(self, expense_type_id: str) -> ExpenseTypePublic:
        if not self._is_valid_object_id(expense_type_id):
            raise HTTPException(status_code=400, detail="Invalid expense type ID format")

        cache_key = f"expense_type:details:{expense_type_id}"

        async def fetch_expense_type():
            expense_type = self.expense_types_collection.find_one({"_id": ObjectId(expense_type_id)})
            if not expense_type:
                raise HTTPException(
                    status_code=404, detail=f"Expense type with ID {expense_type_id} not found"
                )
            return self._format_expense_type(expense_type)

        cached_expense_type = await cache_with_sliding_expiry(cache_key, fetch_expense_type, ttl=300)
        return ExpenseTypePublic(**cached_expense_type)

    async def create_expense_type(self, expense_type: dict) -> ExpenseTypePublic:
        expense_type["created_at"] = datetime.utcnow()
        expense_type["updated_at"] = datetime.utcnow()
        result = self.expense_types_collection.insert_one(expense_type)
        expense_type["_id"] = str(result.inserted_id)

        await invalidate_pattern_cache("expense_types:*")
        return ExpenseTypePublic(**self._format_expense_type(expense_type))

    async def update_expense_type(self, expense_type_id: str, expense_type_update: dict) -> ExpenseTypePublic:
        if not self._is_valid_object_id(expense_type_id):
            raise HTTPException(status_code=400, detail="Invalid expense type ID format")

        expense_type_update["updated_at"] = datetime.utcnow()
        update_result = self.expense_types_collection.update_one(
            {"_id": ObjectId(expense_type_id)}, {"$set": expense_type_update}
        )

        if update_result.matched_count == 0:
            raise HTTPException(
                status_code=404, detail=f"Expense type with ID {expense_type_id} not found"
            )

        updated_expense_type = self.expense_types_collection.find_one({"_id": ObjectId(expense_type_id)})
        await invalidate_cache(f"expense_type:details:{expense_type_id}")
        await invalidate_pattern_cache("expense_types:*")
        return ExpenseTypePublic(**self._format_expense_type(updated_expense_type))

    async def delete_expense_type(self, expense_type_id: str) -> None:
        if not self._is_valid_object_id(expense_type_id):
            raise HTTPException(status_code=400, detail="Invalid expense type ID format")

        delete_result = self.expense_types_collection.delete_one({"_id": ObjectId(expense_type_id)})
        if delete_result.deleted_count == 0:
            raise HTTPException(
                status_code=404, detail=f"Expense type with ID {expense_type_id} not found"
            )

        await invalidate_cache(f"expense_type:details:{expense_type_id}")
        await invalidate_pattern_cache("expense_types:*")

    def _format_expense_type(self, expense_type: dict) -> dict:
        if expense_type is None:
            return {}
        expense_type["id"] = str(expense_type["_id"])
        expense_type.pop("_id", None)
        expense_type["created_at"] = (
            expense_type.get("created_at").isoformat() if "created_at" in expense_type else None
        )
        expense_type["updated_at"] = (
            expense_type.get("updated_at").isoformat() if "updated_at" in expense_type else None
        )
        return expense_type

    @staticmethod
    def _is_valid_object_id(object_id: str) -> bool:
        return bool(re.match(r"^[a-fA-F0-9]{24}$", object_id))

    @staticmethod
    def _get_collection():
        db = client.expense_types_db
        return db["expense_types"]


def get_expense_type_service() -> ExpenseTypeService:
    return ExpenseTypeService(ExpenseTypeService._get_collection())
