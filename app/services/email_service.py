# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
# from app.core.config import settings

# conf = ConnectionConfig(
#     MAIL_USERNAME=settings.EMAIL_USERNAME,
#     MAIL_PASSWORD=settings.EMAIL_PASSWORD,
#     MAIL_FROM=settings.EMAIL_FROM,
#     MAIL_PORT=settings.EMAIL_PORT,
#     MAIL_SERVER=settings.EMAIL_SERVER,
#     MAIL_TLS=True,
#     MAIL_SSL=False,
# )

# async def send_password_reset_email(email: str, token: str):
#     reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
#     message = MessageSchema(
#         subject="Password Reset Request",
#         recipients=[email],
#         body=f"Click the link to reset your password: {reset_url}",
#     )
#     fm = FastMail(conf)
#     await fm.send_message(message)