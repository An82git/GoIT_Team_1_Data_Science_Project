from fastapi import FastAPI, APIRouter, HTTPException
from sqlalchemy import text
from app.settings import settings
from app.db import DBConnectionDep
from datetime import datetime, UTC
from users.routers import session_router, user_router, profile_router
from license_plates.routers import license_plate_router, visit_router
from paymets.routers import payments_router
import uvicorn

app = FastAPI()

base_router = APIRouter(tags=['base'])

routers = [base_router, session_router, profile_router, user_router, license_plate_router, visit_router, payments_router]

@base_router.get("/")
def status(db: DBConnectionDep):
    try:
        result = db.execute(text("SELECT 1"))
        print(result)
        return {"version": settings.app.VERSION, "name": settings.app.NAME, "status": "ok", "env": settings.app.ENV, "datetime": datetime.now(UTC)}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error db connection")

[app.include_router(router, prefix=settings.app.BASE_URL_PREFIX) for router in routers]

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.app.HOST, port=settings.app.PORT, reload=settings.app.ENV == "local")



    