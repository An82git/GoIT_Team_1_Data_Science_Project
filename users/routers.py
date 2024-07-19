
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
    if db.query(User).filter(or_(User.email == body.username, User.username == body.username)).first() is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User banned')
    result =  await auth.authenticate(body, db)
    return result


@session_router.delete('/')
async def logout(db: DBConnectionDep, user: AuthDep, token: str = Depends(auth.oauth2_scheme)):
    return await auth.logout(user, token, db)


@session_router.put('/', response_model=schemas.TokenLoginResponse)
async def refresh_token(db: DBConnectionDep, credentials: HTTPAuthorizationCredentials = Security(security)):
    return await auth.refresh(credentials.credentials, db)


@user_router.post('/', response_model=schemas.UserResponse|None)
async def singup(controller: SessionControllerDep, db: DBConnectionDep, body: schemas.UserCreationModel):
    exist_user = await controller.get_user(email=body.email, db=db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exist')
    body.password = auth.password.hash(body.password)
    user = await controller.create(body, db)
    return user

@user_router.get("/all", response_model=List[schemas.UserResponse]|None, status_code=status.HTTP_200_OK, dependencies=[Depends(auth)])
async def users_list(controller: UsersControllerDep, db: DBConnectionDep):
    return controller.get_users(db)


@user_router.get("/{user_ident}", response_model=schemas.UserModel, status_code=status.HTTP_200_OK, dependencies=[Depends(auth)])
async def read_user_by_name_or_id(user: UserDep):
    return user

@user_router.post("/{user_ident}/license_plate", response_model=license_plates_schemas.LicensePlateResponse, dependencies=[Depends(auth.role_in([UserRoles.ADMIN.value]))], status_code=status.HTTP_201_CREATED)
async def create_license_plate(body: license_plates_schemas.LicensePlate, db: DBConnectionDep, controller: LicensePlateControllerDep, user: UserDep):
    plate = controller.read(body.number, db)
    if plate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='License plate already exists')
    return await controller.create(body, db, user)