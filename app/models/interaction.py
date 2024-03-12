from uuid import uuid4
from sqlalchemy import Column, String, select, DateTime, Boolean, func, ForeignKey, UUID, Integer
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    prompt = Column(String, nullable=False)
    response = Column(String, nullable=False)
    model = Column(String, nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)

    user = relationship("User", back_populates="interactions")

    @classmethod
    async def create(cls, db: AsyncSession, user_id: UUID, prompt: str, response: str,  model: str, prompt_tokens: int, completion_tokens:int, total_tokens: int):
        new_interaction = cls(
            user_id=user_id,
            prompt=prompt,
            response=response,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )
        db.add(new_interaction)
        await db.commit()
        await db.refresh(new_interaction)
        return new_interaction

    @classmethod
    async def find_by_user_id(cls, db: AsyncSession, user_id: UUID):
        result = await db.execute(select(cls).filter(cls.user_id == user_id))
        interactions = result.scalars().all()
        return interactions