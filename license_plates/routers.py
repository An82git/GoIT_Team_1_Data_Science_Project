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
    """
    The function retrieves details of a specific license plate.
    It returns information about the license plate identified by the provided identifier.

    :param plate: License plate instance obtained from the database based on the identifier.
    :type plate: LicensePlateDep
    :return: Information about the license plate.
    :rtype: LicensePlateResponse
    """
    return plate

@license_plate_router.put('/{plate_ident}', response_model=schemas.LicensePlateResponse, dependencies=[Depends(auth.role_in([UserRoles.ADMIN.value]))])
async def update_license_plate(plate: LicensePlateDep, body: schemas.LicensePlate, controller: LicensePlateControllerDep, db: DBConnectionDep):
    """
    The function updates details of an existing license plate.
    It verifies the user has the necessary admin role and updates the license plate with new information.

    :param plate: Existing license plate instance to be updated.
    :type plate: LicensePlateDep
    :param body: New details for the license plate.
    :type body: LicensePlate
    :param controller: License plate management controller.
    :type controller: LicensePlateControllerDep
    :param db: Database connection instance.
    :type db: DBConnectionDep
    :return: Updated license plate information.
    :rtype: LicensePlateResponse
    """
    return await controller.update(plate, body, db)

@license_plate_router.delete('/{plate_ident}', response_model=schemas.LicensePlateResponse, dependencies=[Depends(auth.role_in([UserRoles.ADMIN.value]))])
async def remove_license_plate(plate: LicensePlateDep, controller: LicensePlateControllerDep, db: DBConnectionDep):
    """
    The function deletes a specific license plate from the system.
    It requires the user to have admin privileges to perform the deletion.

    :param plate: License plate instance to be removed.
    :type plate: LicensePlateDep
    :param controller: License plate management controller.
    :type controller: LicensePlateControllerDep
    :param db: Database connection instance.
    :type db: DBConnectionDep
    :return: Information about the deleted license plate.
    :rtype: LicensePlateResponse
    """
    return await controller.remove(plate, db)

@license_plate_router.get('/', response_model=List[schemas.LicensePlateResponse],)
async def read_user_plates(controller: LicensePlateControllerDep, db: DBConnectionDep, user: AuthDep, skip: int = 0, limit: int = 100):
    """
    The function retrieves a list of license plates associated with the authenticated user.
    It supports pagination with skip and limit parameters to control the number of plates retrieved.

    :param controller: License plate management controller.
    :type controller: LicensePlateControllerDep
    :param db: Database connection instance.
    :type db: DBConnectionDep
    :param user: Authenticated user for whom to retrieve license plates.
    :type user: AuthDep
    :param skip: Number of records to skip for pagination.
    :type skip: int
    :param limit: Maximum number of records to retrieve.
    :type limit: int
    :return: List of license plates associated with the user.
    :rtype: List[LicensePlateResponse]
    """
    return await controller.list(db, skip, limit, user)

@license_plate_router.get('/{plate_ident}/visits', response_model=List[schemas.VisitResponse])
async def read_visits(db: DBConnectionDep, controller: LicensePlateControllerDep, plate: UserLicensePlateDep):
    """
    The function retrieves a list of visits associated with a specific license plate.
    It provides details about visits recorded for the given plate.

    :param db: Database connection instance.
    :type db: DBConnectionDep
    :param controller: License plate management controller.
    :type controller: LicensePlateControllerDep
    :param plate: License plate instance for which to retrieve visits.
    :type plate: UserLicensePlateDep
    :return: List of visits associated with the license plate.
    :rtype: List[VisitResponse]
    """
    return await controller.read_visits(plate, db)

@visit_router.post('/', response_model=schemas.VisitResponse, status_code=status.HTTP_201_CREATED)
async def handle_visit(db: DBConnectionDep, controller: LicensePlateControllerDep, user: AuthDep, photo: UploadFile, plate: Optional[str] = Form(None)):
    """
    The function processes a visit event by handling the uploaded photo and optional plate identifier.
    It creates a new visit record and associates it with the provided license plate if it exists.

    :param db: Database connection instance.
    :type db: DBConnectionDep
    :param controller: License plate management controller.
    :type controller: LicensePlateControllerDep
    :param user: Authenticated user handling the visit.
    :type user: AuthDep
    :param photo: Uploaded photo file associated with the visit.
    :type photo: UploadFile
    :param plate: Optional license plate identifier for associating the visit.
    :type plate: Optional[str]
    :return: Information about the created visit record.
    :rtype: VisitResponse
    :raises HTTPException: If the photo is invalid or the license plate is not found.
    """
    try:
        return await controller.handle_visit(photo, plate, db, user)
    except PlateNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Bad photo or Plate not found. Please register it!')
    
