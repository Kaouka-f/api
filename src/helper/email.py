import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

EMAIL_PASSWORD = os.environ.get("")

def send_confirmation_email(user_email, confirmation_link):
    password = str(os.environ.get("kaouka97_password"))
    from_email = 'kaouka97@outlook.com'
    subject = 'Kaouka: Confirmation d\'inscription'
    # Créer le corps du message avec le lien de confirmation
    body = f'Cliquez sur le lien suivant pour confirmer votre inscription : {
        confirmation_link}'
    # Créer l'e-mail
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = user_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    # Envoyer l'e-mail via SMTP
    smtp_server = 'smtp.office365.com'
    smtp_port = 587
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, user_email, msg.as_string())


def send_email(user_email, header, message):
    from_email = 'kaouka97@outlook.com'
    subject = header
    # Créer le corps du message avec le lien de confirmation
    body = message
    # Créer l'e-mail
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = user_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    # Envoyer l'e-mail via SMTP
    smtp_server = 'smtp.office365.com'
    smtp_port = 587
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, 'zEpja6-zedsax-duswew')
        server.sendmail(from_email, user_email, msg.as_string())
