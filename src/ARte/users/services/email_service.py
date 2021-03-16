import smtplib
import environ
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


env = environ.Env()


class EmailService:
    def __init__(self, email_message):
        print(env("JANDIG_EMAIL"))
        self.jandig_email = env("JANDIG_EMAIL")
        self.jandig_email_password = env("JANDIG_EMAIL_PASSWORD")
        self.email_message = email_message

    def send_email_to_recover_password(self, multipart_message):
        email_server = smtplib.SMTP("smtp.gmail.com: 587")
        email_server.starttls()
        email_server.login(multipart_message["From"], self.jandig_email_password)
        email_server.sendmail(
            multipart_message["From"],
            multipart_message["To"],
            multipart_message.as_string(),
        )
        email_server.quit()

    def build_multipart_message(self, user_email):
        multipart_message = MIMEMultipart()
        multipart_message["From"] = self.jandig_email
        multipart_message["To"] = "{}".format(user_email)
        multipart_message["Subject"] = "Recover Password"

        multipart_message.attach(MIMEText(self.email_message, "plain"))
        return multipart_message
