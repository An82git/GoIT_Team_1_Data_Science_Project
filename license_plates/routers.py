from fastapi import APIRouter, Depends, status
from license_plates import schemas
from app.db import DBConnectionDep
from license_plates.dependencies import LicensePlateControllerDep, LicensePlateDep
from app.services.auth import AuthDep, auth
from users.models import UserRoles

license_plate_router = APIRouter(prefix='/license-plates', tags=['license-plates'])
visits_router = APIRouter(prefix='/{plate_ident}/visits', tags=['visits'])

@license_plate_router.get('/{plate_ident}', response_model=schemas.LicensePlateResponse)
async def read_license_plate(plate: LicensePlateDep):
    return plate

@license_plate_router.put('/{plate_ident}', response_model=schemas.LicensePlateResponse, dependencies=[Depends(auth.role_in(UserRoles.ADMIN.value))])
async def update_license_plate(plate: LicensePlateDep, body: schemas.LicensePlate, controller: LicensePlateControllerDep, db: DBConnectionDep):
    return controller.update(plate, body, db)

@license_plate_router.delete('/{plate_ident}', response_model=schemas.LicensePlateResponse)
async def remove_license_plate(plate: LicensePlateDep, controller: LicensePlateControllerDep, db: DBConnectionDep):
    return controller.remove(plate, db)

@visits_router.post('/', response_model=schemas.VisitResponse, status_code=status.HTTP_201_CREATED)
async def create_visit(body: schemas.Visit):
    pass

license_plate_router.include_router(visits_router)