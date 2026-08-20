from fastapi import FastAPI
from app.routers.leads import router as leads_router


from datetime import datetime, timezone


app = FastAPI()
app.include_router(leads_router)


