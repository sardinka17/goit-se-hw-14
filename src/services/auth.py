from typing import Optional
from datetime import datetime, timedelta

import redis
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.database.db import get_postgres_db
from src.repository import users as repository_users
from src.conf.config import settings


class Auth:
    """
    Class for managing authentication and authorization, including password verification,
    creation and decoding of access and refresh tokens, and getting the current user.
    """
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth_scheme = OAuth2PasswordBearer(tokenUrl='api/auth/login')
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        Verify a plain password against a hashed password.

        :param plain_password: The plain text password to verify
        :type plain_password: str
        :param hashed_password: The hashed password to verify against.
        :type hashed_password: str
        :return: True if the password matches, False otherwise.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hash a password.

        :param password: The plain text password to hash.
        :type password: str
        :return: The hashed password.
        :rtype: str
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create an access token.

        :param data: The data to include in the token.
        :type data: dict
        :param expires_delta: The optional expiration time for the token in seconds.
        :type expires_delta: float
        :return: The encoded access token.
        :rtype: str
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'access_token'})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a refresh token.

        :param data: The data to include in the token.
        :type data: dict
        :param expires_delta: The optional expiration time for the token in seconds.
        :type expires_delta: float
        :return: The encoded refresh token.
        :rtype: str
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'refresh_token'})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode a refresh token.

        :param refresh_token: The encoded refresh token.
        :type refresh_token: str
        :return: The email extracted from the token if valid.
        :rtype: str
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            if payload['scope'] == 'refresh_token':
                email = payload['sub']

                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth_scheme), db: Session = Depends(get_postgres_db)):
        """
        Get the current user from the access token.

        :param token: The access token from the request.
        :type token: str
        :param db: The database session.
        :type db: Session
        :return: The current user.
        :rtype: User
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            if payload['scope'] == 'access_token':
                email = payload['sub']

                if not email:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)

        if not user:
            raise credentials_exception

        return user

    def create_email_token(self, data: dict):
        """
        Create a token for email verification.

        :param data: The data to include in the token.
        :type data: dict
        :return: The encoded email token.
        :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return token

    async def get_email_from_token(self, token: str):
        """
        Decode an email token.

        :param token: The encoded email token.
        :type token: str
        :return: The email extracted from the token if valid.
        :rtype: str
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload['sub']

            return email
        except JWTError as error:
            print(error)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Invalid token for email verification'
            )


auth_service = Auth()
