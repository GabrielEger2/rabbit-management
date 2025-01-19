from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, Depends
from schemas import (
    ReimbursementPublic,
    ReimbursementsPublic,
    ReimbursementCreate,
    ReimbursementUpdate,
)
from common.rabbitMQ import get_reimbursements_rabbitmq
from common.postgres import paginate_query, get_db
from typing import Optional


class ReimbursementService:
    def __init__(self, db_session: AsyncSession, reimbursements_rabbitmq):
        self.db_session = db_session
        self.reimbursements_rabbitmq = reimbursements_rabbitmq

    async def get_reimbursements(
        self, page: int, status: Optional[str]
    ) -> ReimbursementsPublic:
        query = select(ReimbursementModel)
        if status:
            query = query.where(ReimbursementModel.status == status)

        reimbursements = await paginate_query(self.db_session, query, page, 26)
        data = [ReimbursementPublic.from_orm(r) for r in reimbursements]

        next_page = page + 1 if len(data) > 25 else None
        return ReimbursementsPublic(data=data[:25], page=page, next=next_page)

    async def get_reimbursement(self, reimbursement_id: int) -> ReimbursementPublic:
        query = await self.db_session.execute(
            select(ReimbursementModel).where(ReimbursementModel.id == reimbursement_id)
        )
        reimbursement = query.scalars().first()
        if not reimbursement:
            raise HTTPException(status_code=404, detail="Reimbursement not found")
        return ReimbursementPublic.from_orm(reimbursement)

    async def create_reimbursement(self, reimbursement_in: ReimbursementCreate):
        self.reimbursements_rabbitmq.publish(
            message=reimbursement_in.dict(),
            routing_key="reimbursements.queue",
            headers={
                "event": "reimbursement.submitted",
                "user": "1"
            },
        )

        return {"message": f"Reimbursement request submitted for user {reimbursement_in.user_id}"}

    async def update_reimbursement(
        self, reimbursement_id: int, reimbursement_update: ReimbursementUpdate
    ):
        query = await self.db_session.execute(
            select(ReimbursementModel).where(ReimbursementModel.id == reimbursement_id)
        )
        reimbursement = query.scalars().first()
        if not reimbursement:
            raise HTTPException(status_code=404, detail="Reimbursement not found")

        for key, value in reimbursement_update.dict(exclude_unset=True).items():
            setattr(reimbursement, key, value)

        await self.db_session.commit()
        await self.db_session.refresh(reimbursement)
        return ReimbursementPublic.from_orm(reimbursement)

def get_reimbursement_service(
    db_session: AsyncSession = Depends(get_db), reimbursements_rabbitmq=Depends(get_reimbursements_rabbitmq)
) -> ReimbursementService:
    return ReimbursementService(db_session, reimbursements_rabbitmq)
