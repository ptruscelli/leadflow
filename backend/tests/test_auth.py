from datetime import datetime, timezone, timedelta
import hashlib
from unittest.mock import AsyncMock
from sqlalchemy import select


from conftest import TestingSessionLocal
from app.models import MagicLink
from app.config import settings


ALLOWED_TEST_EMAIL = "test@example.com" 
TEST_RAW_TOKEN = "test_raw_token"


# login/session tests will need a known raw token
# which POST /magic-link does not give, for security (normally sends it in the email/log)
# so this helper function inserts valid magic link into db and provides a raw token
def insert_magic_link(*, email: str, raw_token: str, expired: bool = False):

    now = datetime.now(timezone.utc)
    db = TestingSessionLocal() # test db

    try:
        db.add(MagicLink(
            email=email,
            token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
            created_at=now,
            expires_at=(
                now - timedelta(minutes=1) if expired 
                else now + timedelta(minutes=10)
            )
        ))
        db.commit()
    finally:
        db.close()



# Test GET /leads but without a session cookie
def test_get_leads_without_session(unauthorized_client):

    response = unauthorized_client.get("/leads")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}



# Test login flow
# insert valid link -> login -> GET /leads  
def test_login_flow(unauthorized_client, monkeypatch):

    # temporarily set allowed email for testing, GET /leads needs it for require_session
    monkeypatch.setattr(settings, "staff_allowlist", ALLOWED_TEST_EMAIL)    

    insert_magic_link(email=ALLOWED_TEST_EMAIL, raw_token=TEST_RAW_TOKEN, expired=False)

    # login
    login_response = unauthorized_client.post("/auth/login", json={
        "raw_token": TEST_RAW_TOKEN
    })
    assert login_response.status_code == 200
    assert login_response.json() == {"message": "Login successful"}
    assert "session" in login_response.cookies

    get_leads_response = unauthorized_client.get("/leads")
    assert get_leads_response.status_code == 200



# POST magic link for unauthorized email returns 200 with regular message
# in same test can check allowed email does create a row
# and hashed token is stored not a raw
def test_post_magic_link(unauthorized_client, monkeypatch):

    # temporarily set allowed email for testing, POST /magic-link needs it for allowlist check
    monkeypatch.setattr(settings, "staff_allowlist", ALLOWED_TEST_EMAIL)    

    # mock send_email so resend api is not called
    monkeypatch.setattr("app.routers.auth.send_email", AsyncMock())

    # magic link attempt for unauthorized email
    send_link_response = unauthorized_client.post("/auth/magic-link", json={
        "email": "unauthorized@email.com"
        })

    # should still return 200 with regular message
    assert send_link_response.status_code == 200
    assert send_link_response.json() == {"message": "If email is allowed, magic link sent"}

    # should not have created a row in db
    db = TestingSessionLocal()
    try:
        assert db.scalars(select(MagicLink)).all() == []
    finally:
        db.close()

    # magic link attempt for allowed email
    send_link_response = unauthorized_client.post("/auth/magic-link", json={
        "email": ALLOWED_TEST_EMAIL
        })
    assert send_link_response.status_code == 200
    assert send_link_response.json() == {"message": "If email is allowed, magic link sent"}

    
    db = TestingSessionLocal()
    try:
        rows = db.scalars(select(MagicLink)).all()
        assert len(rows) == 1 # row should have been created
        assert rows[0].email == ALLOWED_TEST_EMAIL # email matches
        assert len(rows[0].token_hash) == 64  # hashed token should be 64 characters
    finally:
        db.close()




# Test expired magic link
# expect 401 with detail Invalid or expired login link
def test_expired_magic_link(unauthorized_client):
    insert_magic_link(email=ALLOWED_TEST_EMAIL, raw_token=TEST_RAW_TOKEN, expired=True)
    response = unauthorized_client.post("/auth/login", json={
        "raw_token": TEST_RAW_TOKEN
    })
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired login link"}


# Test magic links single use
# login, then login again
# also try with a random token
def test_magic_link_single_use(unauthorized_client):
    insert_magic_link(email=ALLOWED_TEST_EMAIL, raw_token=TEST_RAW_TOKEN, expired=False)
    
    # first login should succeed
    response = unauthorized_client.post("/auth/login", json={
        "raw_token": TEST_RAW_TOKEN
    })
    
    assert response.status_code == 200
    assert response.json() == {"message": "Login successful"}
    
    # second login attempt with same token should fail
    response = unauthorized_client.post("/auth/login", json={
        "raw_token": TEST_RAW_TOKEN
    })
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired login link"}


    # login attempt with random token should fail
    response = unauthorized_client.post("/auth/login", json={
        "raw_token": "random_token"
    })
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired login link"}




# test logout kills the session
# login, logout, try GET /leads
def test_logout(unauthorized_client):

    insert_magic_link(email=ALLOWED_TEST_EMAIL, raw_token=TEST_RAW_TOKEN, expired=False)

    # login
    login_response = unauthorized_client.post("/auth/login", json={
        "raw_token": TEST_RAW_TOKEN
    })
    session_cookie = login_response.cookies["session"] # save cookie for GET /leads
    assert login_response.status_code == 200
    assert login_response.json() == {"message": "Login successful"}

    # logout
    logout_response = unauthorized_client.post("/auth/logout")
    assert logout_response.status_code == 200
    assert logout_response.json() == {"message": "Logout successful"}

    # try GET /leads with deleted cookie
    unauthorized_client.cookies.set("session", session_cookie)
    get_leads_response = unauthorized_client.get("/leads")
    assert get_leads_response.status_code == 401
    assert get_leads_response.json() == {"detail": "Unauthorized"}
