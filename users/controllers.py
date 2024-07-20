from typing import List, Optional
from sqlalchemy.orm import Session

from users import schemas
from app.db import DBConnectionDep
from users.models import UserRoles, User


class SessionController:
    base_model = User

    async def get_user(self, email: str, db: Session) -> base_model | None:
        return db.query(self.base_model).filter(self.base_model.email == email).first()
        
    async def create(self, body: schemas.UserCreationModel, db: Session) -> base_model:
        if db.query(self.base_model).count() == 0:
            user = self.base_model(**body.model_dump(), role=UserRoles.ADMIN)
        else:
            user = self.base_model(**body.model_dump()) 
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
class UsersController:
    base_model = User

    def get_users(self, db: DBConnectionDep) -> Optional[List[User]]:
        return db.query(self.base_model).all()

    async def get_user(self, user_ident: int | str, db: DBConnectionDep) -> User | None:
        query = db.query(self.base_model)
        try:
            user_ident = int(user_ident)
        except:
            pass
        query = query.filter(self.base_model.id == user_ident) if isinstance(user_ident, int) else query.filter(self.base_model.username == user_ident)
        return query.first()