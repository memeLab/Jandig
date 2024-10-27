import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings


class EmailService:
    def __init__(self, email_message):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.jandig_email = settings.SMTP_EMAIL
        self.jandig_email_password = settings.SMTP_PASSWORD
        self.email_message = email_message

    def send_email_to_recover_password(self, multipart_message):
        email_server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        email_server.starttls()
        email_server.login(self.jandig_email, self.jandig_email_password)
        email_server.sendmail(
            multipart_message["From"],
            multipart_message["To"],
            multipart_message.as_string(),
        )
        email_server.quit()

    def build_multipart_message(self, user_email):
        multipart_message = MIMEMultipart("alternative")
        multipart_message["From"] = f"Jandig <{self.jandig_email}>"
        multipart_message["To"] = "{}".format(user_email)
        multipart_message["Subject"] = "Recover Password"

        multipart_message.attach(MIMEText(self.email_message, "plain"))
        return multipart_message
