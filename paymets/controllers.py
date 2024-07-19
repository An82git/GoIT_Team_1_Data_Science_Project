import math
from fastapi import BackgroundTasks
from app.services.mail.payment_email import PaymentEmail
from sqlalchemy.orm import Session
from sqlalchemy import func
from paymets.models import Payment, Price
from license_plates.models import Visit
from users.models import User

class BadVisitException(Exception):
    pass

class PaymentsController:
    async def create_payment(self, visit: Visit, db: Session, user: User) -> Payment:
        if visit.out_at is None:
            raise BadVisitException
        park_time = math.ceil((visit.out_at - visit.in_at).seconds / 3600)
        price = await self.calc_price(park_time, db)
        payment = Payment(total_cost=price, visit=visit)
        db.add(payment)
        db.commit()
        db.refresh(payment)
        self.send_mail(user, payment)
        return payment
    
    def send_mail(self, user: User, payment: Payment):
        bg_task = BackgroundTasks()
        bg_task.add_task(
            PaymentEmail(user.email),
            username = user.username,
            car = payment.visit.license_plate.model,
            license_plate = payment.visit.license_plate.number,
            date_from = payment.visit.in_at,
            date_to = payment.visit.out_at,
            host = 'http://localhost:8000',
            payment_id = payment.id
        )
        if user != payment.visit.license_plate.user:
            self.send_mail(payment.visit.license_plate.user, payment)

    async def calc_price(self, park_time: int, db: Session, previous_price: float = 0.0) -> float:
        price = db.query(Price).order_by(func.abs(Price.hours - park_time)).first()
        total_time = park_time // price.hours
        next_price = previous_price + price
        if total_time != 0:
            return await self.calc_price(park_time - total_time, db, next_price)
        return next_price