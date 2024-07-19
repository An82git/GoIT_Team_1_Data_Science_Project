from fastapi import UploadFile
from datetime import datetime, UTC
from typing import List
from sqlalchemy import or_
from sqlalchemy.orm import Session
from license_plates import schemas
from license_plates.models import LicensePlate, Visit
from users.models import User

class PlateNotFoundException(Exception):
    pass

class LicensePlateController:
    async def list(self, db: Session, skip: int, limit: int, user: User | None = None) -> List[LicensePlate]:
        query = db.query(LicensePlate)
        if user:
            query = query.filter(LicensePlate.user == user)
        return query.offset(skip).limit(limit).all()

    async def read(self, plate_ident: str | int, db: Session, user: User | None = None) -> LicensePlate | None:
        query = db.query(LicensePlate)
        if user:
            query = query.filter(LicensePlate.user == user)
        return query.filter(or_(LicensePlate.id == plate_ident, LicensePlate.number == plate_ident)).first()

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
    
    async def read_visits(self, plate: LicensePlate, db: Session) -> List[Visit]:
        return db.query(Visit).filter(Visit.license_plate == plate).all()
    
    async def handle_visit(self, photo: UploadFile | None, plate: str | None, db: Session, user: User) -> Visit:
        plate_number = plate or photo # тут потрібно буде витягнути номерний знак з фото
        plate = await self.read(plate_number, db)
        if plate is None:
            raise PlateNotFoundException
        visit = db.query(Visit).filter(Visit.license_plate == plate, Visit.out_at == None).first()
        if visit:
            visit.out_at = datetime.now(UTC)
            # створення рахунку і відправка його на емейл 1 або 2 користувачам
        else:
            visit = Visit(license_plate=plate)
            db.add(visit)
        db.commit()
        db.refresh(visit)
        return visit