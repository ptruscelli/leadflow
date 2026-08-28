from fastapi import FastAPI
import logging
from app.routers.leads import router as leads_router
from app.routers.auth import router as auth_router

app = FastAPI()
app.include_router(leads_router)
app.include_router(auth_router)

logging.basicConfig(level=logging.INFO)
