from sqlalchemy import select, func
from typing import Dict, Any, Optional


async def get_total_count(db_session, query) -> int:
    total_count_query = select(func.count()).select_from(query.subquery())
    total_count_result = await db_session.execute(total_count_query)
    return total_count_result.scalar()


async def paginate_query(
    db_session, query, page: int, page_size: int
) -> Dict[str, Any]:
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db_session.execute(query)
    return result.scalars().all()


async def cursor_paginate_query(
    db_session,
    query,
    page_size: int,
    cursor: Optional[Any] = None,
    cursor_column: str = "id",
) -> Dict[str, Any]:
    if cursor:
        query = query.where(
            getattr(query.column_descriptions[0]["entity"], cursor_column) > cursor
        )

    query = query.order_by(
        getattr(query.column_descriptions[0]["entity"], cursor_column)
    ).limit(page_size)

    result = await db_session.execute(query)
    rows = result.scalars().all()

    next_cursor = None
    if rows:
        next_cursor = getattr(rows[-1], cursor_column)

    return {"results": rows, "next_cursor": next_cursor}
