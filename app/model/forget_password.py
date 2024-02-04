from pydantic import BaseModel


class ForgetPasswordRequest(BaseModel):
    email: str
