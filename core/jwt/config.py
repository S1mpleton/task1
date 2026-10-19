import os

from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = "JWT_SECRET_KEY"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")