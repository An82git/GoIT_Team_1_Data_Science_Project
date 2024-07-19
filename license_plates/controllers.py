from sqlalchemy import or_
from sqlalchemy.orm import Session
from license_plates import schemas
from license_plates.models import LicensePlate
from users.models import User

class LicensePlateController:
    async def read(self, plate_ident: str | int, db: Session) -> LicensePlate | None:
        return db.query(LicensePlate).filter(or_(LicensePlate.id == plate_ident, LicensePlate.number == plate_ident)).first()

    async def create(self, body: schemas.LicensePlate, db: Session, user: User) -> LicensePlate:
        plate = LicensePlate(**body.model_dump(), user=user)
        db.add(plate)
        db.commit()
        db.refresh(plate)
        return plate
    
    async def update(self, plate: LicensePlate, body: schemas.LicensePlate, db: Session) -> LicensePlate:
        for key, value in body.model_dump().items():
            setattr(plate, key, value)
        db.commit()
        return plate

    async def remove(self, plate: LicensePlate, db: Session) -> LicensePlate:
         db.delete(plate)
         db.commit()
         return plate