from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserModel


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    Retrieve a user from the database by their email address.

    :param email: The email address of the user to retrieve.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user with the specified email, or None if it does not exist.
    :rtype: User | None
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user in the database.

    :param body: The data for the user to create.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: The newly created user.
    :rtype: User
    """
    avatar = None

    try:
        gravatar = Gravatar(body.email)
        avatar = gravatar.get_image()
    except Exception as error:
        print(error)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update the refresh token for a given user in the database.

    :param user: The user object whose refresh token is to be updated.
    :type user: User
    :param token: The new refresh token.
    :type token: str | None
    :param db: The database session.
    :type db: Session
    :return: Returns None.
    :rtype: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm a user's email address in the database.

    :param email: The email address of the user to confirm.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: Returns None.
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str | None, db: Session) -> User:
    """
    Update the avatar URL for a given user in the database.

    :param email: The email address of the user whose avatar is to be updated.
    :type email: str
    :param url: The new avatar URL.
    :type url: str | None
    :param db: The database session.
    :type db: Session
    :return: The updated user object.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()

    return user
