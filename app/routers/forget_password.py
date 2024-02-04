from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import JSONResponse
from starlette.background import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, MessageType
import datetime, timedelta
import jwt
import os
from app.database import User_Message, User
from app.model.forget_password import ForgetPasswordRequest
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

FORGET_PWD_SECRET_KEY = os.getenv("JWT_PRIVATE_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")


def create_reset_password_token(email: str):
    data = {"sub": email, "exp": datetime.utcnow() + timedelta(minutes=10)}
    token = jwt.encode(data, FORGET_PWD_SECRET_KEY, ALGORITHM)
    return token


@router.post("/forget-password")
def forget_password(background_tasks: BackgroundTasks, fpr: ForgetPasswordRequest):
    try:
        user = User.find_one({"email": fpr.email.lower()})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid Email address",
            )

        forget_url_link = (
            f"{settings.APP_HOST}{settings.FORGET_PASSWORD_URL}/{secret_token}"
        )

        email_body = {
            "company_name": settings.MAIL_FROM_NAME,
            "link_expiry_min": settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES,
            "reset_link": forget_url_link,
        }

        message = MessageSchema(
            subject="Password Reset Instructions",
            recipients=[fpr.email],
            template_body=email_body,
            subtype=MessageType.html,
        )

        template_name = "mail/password_reset.html"

        fm = FastMail(mail_conf)
        background_tasks.add_task(fm.send_message, message, template_name)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Email has been sent",
                "success": True,
                "status_code": status.HTTP_200_OK,
            },
        )
    except Exception as e:
        raise CustomHttpException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something Unexpected, Server Error",
            error_level=ErrorLevel.ERROR_LEVEL_2,
        )
