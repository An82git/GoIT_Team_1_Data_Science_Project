from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.db import DBConnectionDep
from license_plates.controllers import LicensePlateController
from license_plates.models import LicensePlate
from app.services.auth import AuthDep

LicensePlateControllerDep = Annotated[LicensePlateController, Depends(LicensePlateController)]

async def read_plate(plate_ident: str | int, controller: LicensePlateControllerDep, db: DBConnectionDep) -> LicensePlate:
    plate = await controller.read(plate_ident, db)
    if plate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="License plate not found")
    return plate

LicensePlateDep = Annotated[LicensePlate, Depends(read_plate)]

async def read_user_plate(plate_ident: str | int, controller: LicensePlateControllerDep, db: DBConnectionDep, user: AuthDep) -> LicensePlate:
    plate = await controller.read(plate_ident, db, user)
    if plate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="License plate not found")
    return plate

UserLicensePlateDep = Annotated[LicensePlate, Depends(read_user_plate)]