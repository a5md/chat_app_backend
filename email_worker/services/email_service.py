import smtplib
from email.message import EmailMessage
from .email_writer import Email_writer
from ..core.config import settings


class Email_sender:

    def __init__(self):
        self.smtp = None
        self.writer = Email_writer()


    def connect(self):

        self.smtp = smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT
        )

        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.ehlo()

        self.smtp.login(
            settings.SMTP_EMAIL,
            settings.SMTP_PASSWORD
        )


    def send(self, job: dict):
        if self.smtp is None:
            self.connect()


        html, subject = self.writer.write(job)
        

        message = EmailMessage()

        message["From"] = settings.SMTP_EMAIL
        message["To"] = job["email"]
        message["Subject"] = subject


        message.set_content(
            "Please use an HTML compatible email client."
        )

        message.add_alternative(
            html,
            subtype="html"
        )


        self.smtp.send_message(message)
        

    def close(self):

        if self.smtp:
            self.smtp.quit()
            self.smtp = None