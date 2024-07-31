
from sqlalchemy import or_
from typing import List
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi import APIRouter, status, Depends, HTTPException, Security

from users import schemas
from users.dependencies import SessionControllerDep, UsersControllerDep, UserDep
from app.db import DBConnectionDep
from users.models import User, UserRoles
from app.services.auth import auth, AuthDep
from license_plates import schemas as license_plates_schemas
from license_plates.dependencies import LicensePlateControllerDep


security = HTTPBearer()


session_router = APIRouter(prefix="/session", tags=['session'])
user_router = APIRouter(prefix="/users", tags=['users'])
profile_router = APIRouter(prefix="/profile", tags=['profile'])


@session_router.post('/', response_model=schemas.TokenLoginResponse)
async def login(db: DBConnectionDep, body:OAuth2PasswordRequestForm=Depends()):
    """
    The login function authenticates a user and returns an access token.
    It takes an OAuth2PasswordRequestForm object containing login credentials,
    verifies the user against the database, and returns an access token if successful.

    :param db: Database connection instance.
    :type db: DBConnectionDep
    :param body: Authentication credentials (username and password).
    :type body: OAuth2PasswordRequestForm
    :return: Access token response object.
    :rtype: TokenLoginResponse
    """
    result =  await auth.authenticate(body, db)
    return result


@session_router.delete('/')
async def logout(db: DBConnectionDep, user: AuthDep, token: str = Depends(auth.oauth2_scheme)):
    """
    The logout function terminates the user's session by invalidating the access token.
    It removes the active token for the user and logs them out of the system.

    :param db: Database connection instance.
    :type db: DBConnectionDep
    :param user: Authenticated user.
    :type user: AuthDep
    :param token: Access token used for authentication.
    :type token: str
    :return: Confirmation of successful logout.
    :rtype: None
    """
    return await auth.logout(user, token, db)


@session_router.put('/', response_model=schemas.TokenLoginResponse)
async def refresh_token(db: DBConnectionDep, credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    The refresh_token function generates a new access token based on the provided old token.
    It accepts the old token and returns a new access token.

    :param db: Database connection instance.
    :type db: DBConnectionDep
    :param credentials: Old access token to be refreshed.
    :type credentials: HTTPAuthorizationCredentials
    :return: New access token response object.
    :rtype: TokenLoginResponse
    """
    return await auth.refresh(credentials.credentials, db)


@user_router.post('/', response_model=schemas.UserResponse|None)
async def singup(controller: SessionControllerDep, db: DBConnectionDep, body: schemas.UserCreationModel):
    """
    The signup function registers a new user in the system.
    It checks if a user with the given email already exists in the database.
    If so, it raises an HTTP 409 conflict error. Otherwise, it hashes the password
    and creates a new user with the provided details.

    :param controller: User management controller.
    :type controller: SessionControllerDep
    :param body: New user information (email, password, etc.).
    :type body: UserCreationModel
    :param db: Database connection instance.
    :type db: DBConnectionDep
    :return: Information about the newly created user.
    :rtype: UserResponse | None
    :raises HTTPException: If a user with the given email already exists.
    """
    exist_user = await controller.get_user(email=body.email, db=db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exist')
    body.password = auth.password.hash(body.password)
    user = await controller.create(body, db)
    return user

@user_router.get("/all", response_model=List[schemas.UserResponse]|None, status_code=status.HTTP_200_OK, dependencies=[Depends(auth)])
async def users_list(controller: UsersControllerDep, db: DBConnectionDep):
    """
    The users_list function retrieves a list of all users from the database.
    It returns a list of user details.

    :param controller: User management controller.
    :type controller: UsersControllerDep
    :param db: Database connection instance.
    :type db: DBConnectionDep
    :return: List of users.
    :rtype: List[UserResponse] | None
    """
    return controller.get_users(db)


@user_router.get("/{user_ident}", response_model=schemas.UserModel, status_code=status.HTTP_200_OK, dependencies=[Depends(auth)])
async def read_user_by_name_or_id(user: UserDep):
    """
    The read_user_by_name_or_id function retrieves user information based on the user identifier.
    It returns details of the authenticated user.

    :param user: Authenticated user.
    :type user: UserDep
    :return: User details.
    :rtype: UserModel
    """
    return user

@user_router.post("/{user_ident}/license_plate", response_model=license_plates_schemas.LicensePlateResponse, dependencies=[Depends(auth.role_in([UserRoles.ADMIN.value]))], status_code=status.HTTP_201_CREATED)
async def create_license_plate(body: license_plates_schemas.LicensePlate, db: DBConnectionDep, controller: LicensePlateControllerDep, user: UserDep):
    """
    The create_license_plate function creates a new license plate for a user.
    It checks if a license plate with the given number already exists in the database.
    If so, it raises an HTTP 409 conflict error. Otherwise, it creates a new license plate.

    :param body: License plate details.
    :type body: LicensePlate
    :param db: Database connection instance.
    :type db: DBConnectionDep
    :param controller: License plate management controller.
    :type controller: LicensePlateControllerDep
    :param user: Authenticated user.
    :type user: UserDep
    :return: Information about the created license plate.
    :rtype: LicensePlateResponse
    :raises HTTPException: If the license plate already exists.
    """
    plate = await controller.read(body.number, db)
    if plate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='License plate already exists')
    return await controller.create(body, db, user)