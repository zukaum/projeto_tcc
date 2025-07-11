import smtplib
from email.mime.text import MIMEText
from .config import SMTP_USER, SMTP_PASS, SMTP_HOST, SMTP_PORT

def send_verification_email(to_email: str, link: str):
    msg = MIMEText(f"Confirme seu cadastro: {link}")
    msg['Subject'] = 'Confirme seu e-mail'
    msg['From'] = SMTP_USER
    msg['To'] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)