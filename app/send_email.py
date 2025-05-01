import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env')

mail_from = os.getenv("GMAIL")
mail_password = os.getenv("GMAILPASSWORD")

def send_email(email_from, email_password, email_to, subject, body):

    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_from, email_password)

        server.sendmail(email_from, email_to, msg.as_string())
        server.quit()

        print("Email sent!")
    except Exception as e:
        print(e)


def send_password_reset_email(email: str, reset_link: str):
    subject = "Password Reset Request"
    body = f"""
    You have requested to reset your password.
    Please click the following link to reset your password:
    {reset_link}

    This link will expire in 30 minutes.
    If you didn't request this, please ignore this email.
    """

    send_email(
        email_from=os.getenv("GMAIL"),
        email_password=os.getenv("GMAILPASSWORD"),
        email_to=email,
        subject=subject,
        body=body
    )