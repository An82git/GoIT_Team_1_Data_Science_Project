
import os
from fastapi import UploadFile
from datetime import datetime, UTC
from typing import List, Optional
from sqlalchemy.orm import Session
from license_plates import schemas
from license_plates.models import LicensePlate, Visit
from users.models import User
from paymets.controllers import PaymentsController
from license_plates.photo2text import read_text
import shutil
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
        try:
            plate_ident = int(plate_ident)
        except:
            pass
        query = query.filter(LicensePlate.id == plate_ident) if isinstance(plate_ident, int) else query.filter(LicensePlate.number == plate_ident)
        return query.first()

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
    

    def extract_plate_number(self, photo: UploadFile) -> str:
        # Збережіть тимчасовий файл
        temp_file = f"temp_{photo.filename}"
        try:
            with open(temp_file, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            
            # Використовуйте temp_file для обробки (наприклад, розпізнавання тексту)
            plate_number = read_text(temp_file)
        finally:
            # Видалення тимчасового файлу
            if os.path.exists(temp_file):
                os.remove(temp_file)

        return plate_number


    async def handle_visit(self, photo: UploadFile | None, plate: str | None, db: Session, user: User) -> Optional[Visit]:
        plate_number = plate #or photo # тут потрібно буде витягнути номерний знак з фото
        if photo:
            print("=============")
            plate_number =  self.extract_plate_number(photo)

        if plate_number is None:
            raise PlateNotFoundException

        print(plate_number)
        plate = await self.read(plate_number, db)
        
        if plate is None:
            raise PlateNotFoundException
        visit =  db.query(Visit).filter(Visit.license_plate == plate, Visit.out_at == None).first()
        if visit:
            payment_controller = PaymentsController()
            visit.out_at = datetime.now(UTC)
            await payment_controller.create_payment(visit, db, user)
        else:
            visit = Visit(license_plate=plate)
            db.add(visit)
        db.commit()
        db.refresh(visit)
        return visit

