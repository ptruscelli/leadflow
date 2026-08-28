""" SQLAlchemy models for database """

from sqlalchemy import Integer, String, MetaData
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s",
        "pk": "pk_%(table_name)s",
    })


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    company: Mapped[str]
    phone: Mapped[str | None] = mapped_column(default=None)
    source: Mapped[str]
    message: Mapped[str]
    status: Mapped[str] = mapped_column(default="new")
    note: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    # need lambda to avoid evaluating datetime.now() at import time
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)



class MagicLink(Base):
    __tablename__ = "magic_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str]
    token_hash: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime]
    used_at: Mapped[datetime | None] = mapped_column(default=None)



class AuthSession(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str]
    token_hash: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime]



