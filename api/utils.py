from django.template.loader import render_to_string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
import random
import string
import smtplib


def generate_password(length=8):
    characters = string.ascii_letters + string.digits #+ string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))

    return password


def send_password_email(user_email, new_password):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Recuperação de senha"
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = user_email

    # Renderiza o template com os dados
    html_message = render_to_string(
        'reset_password.html', {
            'new_password': new_password
        }
    )

    text_message = f'Sua nova senha é: {new_password}'

    part1 = MIMEText(text_message, 'plain', 'utf-8')
    part2 = MIMEText(html_message, 'html', 'utf-8')

    msg.attach(part1)
    msg.attach(part2)

    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(settings.EMAIL_HOST_USER, user_email, msg.as_string())
