from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta

import os

load_dotenv()
ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int (os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(
    data: dict,
    expire_delta: timedelta | None = None
):
    data = data.copy()

    if expire_delta is not None:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    data.update({"exp": expire})

    encoded_jwt = jwt.encode(
        claims=data,
        key=SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt
       
