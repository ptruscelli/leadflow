from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.routers.leads import router as leads_router
from app.routers.auth import router as auth_router
from app.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_domain],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads_router)
app.include_router(auth_router)

logging.basicConfig(level=logging.INFO)
