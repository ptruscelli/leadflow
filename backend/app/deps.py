from fastapi import Depends, HTTPException, Cookie
import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from app.config import settings
from app.database import SessionLocal
from app.models import AuthSession


# dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# dependency to require a valid session cookie
def require_session(
    db: Session = Depends(get_db),
    session: str | None = Cookie(default=None),
):

    if session is None: # no session cookie
        raise HTTPException(status_code=401, detail="Unauthorized")

    hashed_token = hashlib.sha256(session.encode()).hexdigest()
    auth_session = db.scalars(
        select(AuthSession).where(AuthSession.token_hash == hashed_token)
    ).first()

    now = datetime.now(timezone.utc)

    if (
        auth_session is None # check session exists in db
        or auth_session.expires_at.replace(tzinfo=timezone.utc) < now # check session is not expired
        or auth_session.email not in settings.staff_emails # check session is for a valid staff member
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return auth_session.email 