""" SQLAlchemy models for database """

from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass

class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    phone: Mapped[str]
    message: Mapped[str]
    status: Mapped[str] = mapped_column(default="new")
    note: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    # need lambda to avoid evaluating datetime.now() at import time
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)


