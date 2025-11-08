from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)

async def send_password_reset_email(email_to: EmailStr, new_password: str):
    """
    Sends a new temporary password.
    """
    html_content = f"""
    <html>
    <body>
        <h2>비밀번호 재설정</h2>
        <p>비밀번호가 재설정되었습니다. 새로운 임시 비밀번호는 다음과 같습니다:</p>
        <h3 style="color:red;">{new_password}</h3>
        <p>로그인 후 이 비밀번호를 즉시 변경해 주시기 바랍니다.</p>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="새로운 임시 비밀번호 안내",
        recipients=[email_to],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)