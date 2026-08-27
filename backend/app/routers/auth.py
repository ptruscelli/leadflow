from fastapi import APIRouter, Depends, HTTPException, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import secrets
import hashlib
import logging
import asyncio
import resend

from app.schemas import MagicLinkRequest, LoginRequest
from app.deps import get_db
from app.models import MagicLink, AuthSession
from app.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

resend.api_key = settings.resend_api_key

# helper function to send email with Resend API
async def send_email(to_email: str, magic_link: str):

    try:
        await asyncio.to_thread(resend.Emails.send, {
            "from": f"Brightline Login <{settings.resend_sender_email}>",
            "to": [to_email],
            "subject": "Brightline Login Link",
            "html": f"<p><a href='{magic_link}'>Click here to login</a></p>",
            "text": f"Click here to login: {magic_link}", # plain text backup
        })

    except Exception as e:
        logger.error("Failed to send email: %s", e)
        # no raise so that caller continues, returns 200
        # log fallback can still print URL

    


# POST /auth/magic-link

# check allowlist from env
# create hashed token, send email, log URL
# return 200 with the generic message
@router.post("/magic-link", status_code=200)
async def send_magic_link(body: MagicLinkRequest, db: Session = Depends(get_db)):

    if body.email.lower() in settings.staff_emails:

        # raw and hashed token
        raw_token = secrets.token_urlsafe(32)
        hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()

        # create magic link db row
        now = datetime.now(timezone.utc)
        magic_link = MagicLink(
            email=body.email.lower(),
            token_hash=hashed_token, # database only stores hashed tokens for security
            created_at=now,
            expires_at=now + timedelta(minutes=10)
        )
        db.add(magic_link)
        db.commit()
        # (to remember): db.refresh(obj) reloads db object
        # for when you want to access/return the object after db.commit()
        # here just need raw_token for the URL so no need to refresh

        # send email with magic link
        URL = f"{settings.frontend_domain}/auth/login?token={raw_token}"

        await send_email(body.email.lower(), URL)

        if settings.log_magic_links:
            logger.info(f"Magic link sent to {body.email}: {URL}")
         
    return {"message": "If email is allowed, magic link sent"}



  
# POST /auth/login

# hash incoming token and look up
# reject if not found, used, or expired
# set used_at (or delete token as soon as it is validated/used)
# create session
# set cookie, e.g session=raw_session_token
@router.post("/login", status_code=200)
def login(body: LoginRequest, db: Session = Depends(get_db)):

    hashed_token = hashlib.sha256(body.raw_token.encode()).hexdigest() # same as in send_magic_link

    # db lookup for magic link
    magic_link = db.scalars(
        select(MagicLink).where(MagicLink.token_hash == hashed_token)
    ).first()

    now = datetime.now(timezone.utc)

    if (
        magic_link is None # check if token exists
        or magic_link.used_at is not None # check if token has been used
        or magic_link.expires_at.replace(tzinfo=timezone.utc) < now # check if token has expired
    ):
        raise HTTPException(status_code=401, detail="Invalid or expired login link")

    magic_link.used_at = now

    raw_session_token = secrets.token_urlsafe(32)
    session = AuthSession(
        email=magic_link.email,
        token_hash=hashlib.sha256(raw_session_token.encode()).hexdigest(),
        created_at=now,
        expires_at=now + timedelta(hours=8)
    )
    db.add(session)
    db.commit()
    # don't need db.refresh(), similar reason to magic link (above)

    # set cookie and return response
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="session",
        value=raw_session_token,
        httponly=True, # JavaScript cannot read the cookie (stops XSS)
        secure=settings.secure_cookies, # Only sent over HTTPS (if = true in .env)
        samesite="lax", # Prevents CSRF attacks
        max_age=8 * 60 * 60, # 8 hours in seconds (matches db session expiry)
        path="/", # set cookie for all paths
    )
    return response




# POST /auth/logout 
# delete session
# delete cookie
@router.post("/logout", status_code=200)
def logout(
    db: Session = Depends(get_db),
    session:str | None = Cookie(default=None)):

    if session:
        hashed_token = hashlib.sha256(session.encode()).hexdigest()
        auth_session = db.scalars(
            select(AuthSession).where(AuthSession.token_hash == hashed_token)
        ).first()

        if auth_session is not None:
            db.delete(auth_session)
            db.commit()
            
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie(
        key="session",
        path="/",
        samesite="lax",
        secure=settings.secure_cookies,
    )
    return response
