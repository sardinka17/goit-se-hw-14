from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_postgres_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas.users import UserDB

router = APIRouter(prefix='/users', tags=['users'])
cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)


@router.get('/me/', response_model=UserDB)
async def get_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve details of the current authenticated user.

    :param current_user: The user making the request.
    :type current_user: User
    :return: The database model representing the details of the current user.
    :rtype: UserDB
    """
    return current_user


@router.patch('/avatar', response_model=UserDB)
async def update_avatar_user(
        file: UploadFile = File(),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_postgres_db)
):
    """
    Retrieve details of the current authenticated user.

    :param file: The avatar image file to upload.
    :type file: UploadFile
    :param current_user: The user to update avatar for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The updated database model representing the details of the current user with the new avatar.
    :rtype: UserDB
    """
    public_id = f'ContactsApp/{current_user.email}'
    resource = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    resource_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop='fill', version=resource.get('version')
    )
    user = await repository_users.update_avatar(current_user.email, resource_url, db)

    return user
