from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, File, Form, UploadFile
from license_plates import schemas
from app.db import DBConnectionDep
from license_plates.dependencies import LicensePlateControllerDep, LicensePlateDep, UserLicensePlateDep
from license_plates.controllers import PlateNotFoundException
from app.services.auth import auth, AuthDep
from users.models import UserRoles

license_plate_router = APIRouter(prefix='/license-plates', tags=['license-plates'])
visit_router = APIRouter(prefix='/visit', tags=['visit'])

@license_plate_router.get('/{plate_ident}', response_model=schemas.LicensePlateResponse)
async def read_license_plate(plate: LicensePlateDep):
    return plate

@license_plate_router.put('/{plate_ident}', response_model=schemas.LicensePlateResponse, dependencies=[Depends(auth.role_in([UserRoles.ADMIN.value]))])
async def update_license_plate(plate: LicensePlateDep, body: schemas.LicensePlate, controller: LicensePlateControllerDep, db: DBConnectionDep):
    return await controller.update(plate, body, db)

@license_plate_router.delete('/{plate_ident}', response_model=schemas.LicensePlateResponse, dependencies=[Depends(auth.role_in([UserRoles.ADMIN.value]))])
async def remove_license_plate(plate: LicensePlateDep, controller: LicensePlateControllerDep, db: DBConnectionDep):
    return await controller.remove(plate, db)

@license_plate_router.get('/', response_model=List[schemas.LicensePlateResponse],)
async def read_user_plates(controller: LicensePlateControllerDep, db: DBConnectionDep, user: AuthDep, skip: int = 0, limit: int = 100):
    return await controller.list(db, skip, limit, user)

@license_plate_router.get('/{plate_ident}/visits', response_model=List[schemas.VisitResponse])
async def read_visits(db: DBConnectionDep, controller: LicensePlateControllerDep, plate: UserLicensePlateDep):
    return await controller.read_visits(plate, db)

@visit_router.post('/', response_model=schemas.VisitResponse, status_code=status.HTTP_201_CREATED)
async def handle_visit(db: DBConnectionDep, controller: LicensePlateControllerDep, user: AuthDep, photo: UploadFile, plate: Optional[str] = Form(None)):
    if plate is None and photo is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Please send photo or license plate')
    try:
        return await controller.handle_visit(photo, plate, db, user)
    except PlateNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Plate not found. Please register it.')
    
