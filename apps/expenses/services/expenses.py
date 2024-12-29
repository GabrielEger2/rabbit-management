from common.mongo import client
from typing import List, Optional
from datetime import datetime
from schemas import ExpensesPublic, ExpensePublic
from common.redis import (
    cache_with_expiry,
    cache_with_sliding_expiry,
    invalidate_cache,
    invalidate_pattern_cache,
)
from fastapi import HTTPException
import re
from bson import ObjectId

class ExpenseService:
    def __init__(self, expenses_collection: any):
        self.expenses_collection = expenses_collection

    async def get_expenses(self, page: int, order: str, sort: str, type_filter: Optional[str] = None) -> ExpensesPublic:
        cache_key = f"expenses:page={page}:order={order}:sort={sort}:type={type_filter or 'all'}"

        async def fetch_expenses():
            query = self._build_expense_query(type_filter)
            sort_order = -1 if order == "desc" else 1
            sort_field = sort if sort in ["amount", "incurred_date", "created_at"] else "created_at"

            expenses = (
                self.expenses_collection.find(query)
                .sort(sort_field, sort_order)
                .skip((page - 1) * 25)
                .limit(26)
                .to_list(26)
            )

            expenses_public = [ExpensePublic(**self._format_expense(expense)) for expense in expenses]

            next_page = None
            if len(expenses_public) > 25:
                next_page = page + 1
                expenses_public = expenses_public[:25]

            return {
                "data": [expense.dict() for expense in expenses_public],
                "page": page,
                "next": next_page,
            }

        cached_result = await cache_with_expiry(cache_key, fetch_expenses, ttl=300)

        return ExpensesPublic(
            data=[ExpensePublic(**expense) for expense in cached_result["data"]],
            page=cached_result["page"],
            next=cached_result.get("next"),
        )

    async def get_expense(self, expense_id: str) -> ExpensePublic:
        if not self._is_valid_object_id(expense_id):
            raise HTTPException(status_code=400, detail="Invalid expense ID format")

        cache_key = f"expense:details:{expense_id}"

        async def fetch_expense():
            expense = self.expenses_collection.find_one({"_id": ObjectId(expense_id)})
            if not expense:
                raise HTTPException(
                    status_code=404, detail=f"Expense with ID {expense_id} not found"
                )
            return self._format_expense(expense)

        cached_expense = await cache_with_sliding_expiry(cache_key, fetch_expense, ttl=300)
        return ExpensePublic(**cached_expense)

    async def create_expense(self, expense: dict) -> ExpensePublic:
        expense["created_at"] = datetime.utcnow()
        expense["updated_at"] = datetime.utcnow()
        result = self.expenses_collection.insert_one(expense)
        expense["_id"] = str(result.inserted_id)

        await invalidate_pattern_cache("expenses:*")
        return ExpensePublic(**self._format_expense(expense))

    async def update_expense(self, expense_id: str, expense_update: dict) -> ExpensePublic:
        if not self._is_valid_object_id(expense_id):
            raise HTTPException(status_code=400, detail="Invalid expense ID format")

        expense_update["updated_at"] = datetime.utcnow()
        update_result = self.expenses_collection.update_one(
            {"_id": ObjectId(expense_id)}, {"$set": expense_update}
        )

        if update_result.matched_count == 0:
            raise HTTPException(
                status_code=404, detail=f"Expense with ID {expense_id} not found"
            )

        updated_expense = self.expenses_collection.find_one({"_id": ObjectId(expense_id)})
        await invalidate_cache(f"expense:details:{expense_id}")
        await invalidate_pattern_cache("expenses:*")
        return ExpensePublic(**self._format_expense(updated_expense))

    async def delete_expense(self, expense_id: str) -> None:
        if not self._is_valid_object_id(expense_id):
            raise HTTPException(status_code=400, detail="Invalid expense ID format")

        delete_result = self.expenses_collection.delete_one({"_id": ObjectId(expense_id)})
        if delete_result.deleted_count == 0:
            raise HTTPException(
                status_code=404, detail=f"Expense with ID {expense_id} not found"
            )

        await invalidate_cache(f"expense:details:{expense_id}")
        await invalidate_pattern_cache("expenses:*")

    def _build_expense_query(self, type_filter: Optional[str]) -> dict:
        query = {}
        if type_filter:
            query["type"] = type_filter
        return query

    def _format_expense(self, expense: dict) -> dict:
        if expense is None:
            return {}
        expense["id"] = str(expense["_id"])
        expense.pop("_id", None)
        expense["created_at"] = (
            expense.get("created_at").isoformat() if "created_at" in expense else None
        )
        expense["updated_at"] = (
            expense.get("updated_at").isoformat() if "updated_at" in expense else None
        )
        return expense

    @staticmethod
    def _is_valid_object_id(object_id: str) -> bool:
        return bool(re.match(r"^[a-fA-F0-9]{24}$", object_id))

    @staticmethod
    def _get_collection():
        db = client.expenses_db
        return db["expenses"]


def get_expense_service() -> ExpenseService:
    return ExpenseService(ExpenseService._get_collection())
