import smtplib
import ssl
from email.mime.text import MIMEText

from internal import interface

class SmtpClient(interface.ISmtpClient):
    def __init__(self, email: str, app_password: str):
        self.email = email
        self.app_password = app_password
        self.smtp_server = "smtp.yandex.ru"
        self.port = 465
        self.use_ssl = True

    def send_message(self, recipient_email: str, text: str):
        msg = MIMEText(text, 'plain', 'utf-8')
        msg['From'] = self.email
        msg['To'] = recipient_email
        msg['Subject'] = 'Wazzio'

        context = ssl.create_default_context()

        if self.use_ssl:
            # Яндекс - прямое SSL соединение
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
                server.login(self.email, self.app_password)
                server.send_message(msg)


if __name__ == "__main__":
    smtp_client = SmtpClient("Metro4akin@yandex.ru", "pqkgbovngwynutyi")
    smtp_client.send_message("lscmrr20@gmail.com", "Hello")