from app.services.mail import SendMail

class PaymentEmail(SendMail):
    subject = 'Будь-ласка, оплатіть Ваш рахунок за стоянку'
    template = "payment_email.html"