from fastapi import APIRouter, HTTPException, Depends, Security, BackgroundTasks, Request, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_postgres_db
from src.repository import users as repository_users
from src.schemas.users import UserModel, UserResponse, TokenModel
from src.schemas.email import RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email


router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel,
                 background_tasks: BackgroundTasks,
                 request: Request,
                 db: Session = Depends(get_postgres_db)
                 ):
    """
    Register a new user.

    :param body: The data schema containing user registration details.
    :type body: UserModel
    :param background_tasks: Sends confirmation emails.
    :type background_tasks: BackgroundTasks
    :param request: Gets the base URL for email links.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: The newly created user details and a success message.
    :rtype: dict
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)

    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exists')

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)

    return {'user': new_user, 'detail': "User successfully created. Check your email for confirmation."}


@router.post('/login', response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_postgres_db)):
    """
    Authenticate and login a user.

    :param body: TThe data schema containing user login credentials (username and password).
    :type body: OAuth2PasswordRequestForm
    :param db: The database session.
    :type db: Session
    :return: A dictionary containing the access token, refresh token, and token type ('bearer').
    :rtype: dict
    """
    user = await repository_users.get_user_by_email(body.username, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email not confirmed')

    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

    access_token = await auth_service.create_access_token(data={'sub': user.email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': user.email})
    await repository_users.update_token(user, refresh_token, db)

    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: Session = Depends(get_postgres_db)
):
    """
    Refresh the access token using a refresh token.

    :param credentials: The HTTP Authorization credentials containing the refresh token.
    :type credentials: HTTPAuthorizationCredentials
    :param db: The database session.
    :type db: Session
    :return: The new access token, the new refresh token, and the token type ('bearer').
    :rtype: dict
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')

    access_token = await auth_service.create_access_token(data={'sub': email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': email})
    await repository_users.update_token(user, refresh_token, db)

    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_postgres_db)):
    """
     Confirm a user's email using a verification token.

    :param token: The verification token extracted from the URL path.
    :type token: str
    :param db: The database session.
    :type db: Session
    :return: The message indicating whether the email was already confirmed or has been successfully confirmed.
    :rtype: dict
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')

    if user.confirmed:
        return {'message': 'Your email is already confirmed'}

    await repository_users.confirmed_email(email, db)

    return {'message': 'Email confirmed'}


@router.post('/request_email')
async def request_email(body: RequestEmail,
                        background_tasks: BackgroundTasks,
                        request: Request,
                        db: Session = Depends(get_postgres_db)
                        ):
    """
    Request email confirmation.

    :param body: The data schema containing the email address to send the confirmation email to.
    :type body: RequestEmail
    :param background_tasks: Sends the confirmation email.
    :type background_tasks: BackgroundTasks
    :param request: Gets the base URL for email links.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: The message indicating whether the email is already confirmed,
              or instructing the user to check their email for confirmation.
    :rtype: dict
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {'message': 'Your email is already confirmed'}

    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)

    return {'message': 'Check your email for confirmation'}
