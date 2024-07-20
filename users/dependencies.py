from fastapi import Depends, HTTPException, status
from typing import Annotated
from users.controllers import SessionController, UsersController
from app.db import DBConnectionDep
from users.models import User


UsersControllerDep = Annotated[UsersController, Depends(UsersController)]
SessionControllerDep = Annotated[SessionController, Depends(SessionController)]

async def read_user(user_ident: str | int, db: DBConnectionDep, controller: UsersControllerDep) -> User:
    user = await controller.get_user(user_ident, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

UserDep = Annotated[User, Depends(read_user)]