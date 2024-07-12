from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME='Contacts',
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Send a verification email to the user.

    :param email: The email address of the recipient.
    :type email: EmailStr
    :param username: The username of the recipient.
    :type username: str
    :param host: The host URL to be included in the email.
    :type host: str
    :return: Returns None.
    :rtype: None
    """
    try:
        token_verification = auth_service.create_email_token({'sub': email})
        message = MessageSchema(
            subject='Confirm your email',
            recipients=[email],
            template_body={'host': host, 'username': username, 'token': token_verification},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name='verify_email.html')  # template_name = verify_email.html
    except ConnectionErrors as error:
        print(error)
