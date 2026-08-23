from fastapi import FastAPI
from app.routers.leads import router as leads_router


app = FastAPI()
app.include_router(leads_router)


