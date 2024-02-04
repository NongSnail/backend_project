from fastapi import FastAPI, Depends, HTTPException, status
from app.azure_openai import generate_message
from fastapi.middleware.cors import CORSMiddleware
from app.model.user import UserMessage
from app.routers import auth, user
from app.database import User_Message, User
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
import jwt
from .config import settings
import base64


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = jwt.decode(
            jwt=token,
            key=base64.b64decode(settings.JWT_PUBLIC_KEY).decode("utf-8"),
            algorithms=settings.JWT_ALGORITHM,
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


app.include_router(auth.router, tags=["Auth"], prefix="/api/auth")
app.include_router(user.router, tags=["Users"], prefix="/api/users")


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI with MongoDB"}


@app.post("/api/user_message")
async def root(UserMessage: UserMessage, token: str = Depends(get_current_user)):
    conversation_history = []
    user_id = str(token["sub"])
    if str(UserMessage.content) == "":
        raise HTTPException(status_code=400, detail="message is required")
    if UserMessage.role != "user":
        raise HTTPException(status_code=400, detail="user role only")

    check_user = User.find_one({"_id": ObjectId(user_id)})

    if not check_user:
        raise HTTPException(status_code=404, detail="User not found")

    text = generate_message(str(UserMessage.content))
    conversation_history.append({"role": "user", "content": UserMessage.content})
    conversation_history.append({"role": "assistant", "content": text})

    check_user_id_in_user_message = User_Message.find_one({"_id": ObjectId(user_id)})
    if not check_user_id_in_user_message:
        User_Message.insert_one(
            {
                "_id": ObjectId(user_id),
                "history_message": conversation_history,
            }
        )
    else:
        User_Message.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"history_message": {"$each": conversation_history}}},
            upsert=True,
        )
    return {"role": "assistant", "content": text}


@app.get("/api/history_message")
def root(token: str = Depends(get_current_user)):
    user_message = User_Message.find_one({"_id": ObjectId(str(token["sub"]))})
    if user_message != None:
        data = {"history_message": user_message.get("history_message", [])}
        return data
    return {"history_message": []}


@app.delete("/api/delete_message")
def root(token: str = Depends(get_current_user)):
    User_Message.delete_one({"_id": ObjectId(str(token["sub"]))})


if __name__ == "__main__":
    app.run()
