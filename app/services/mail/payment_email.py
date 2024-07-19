from fastapi_mail import MessageSchema
from app.services.mail import SendMail

class ConfirmationEmail(SendMail):
    subject = 'Будь-ласка, оплатіть Ваш рахунок за стоянку'
    template = "confirm_email.html"