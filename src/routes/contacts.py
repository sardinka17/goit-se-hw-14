from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_postgres_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.schemas.contacts import ContactModel, ContactCreate, ContactUpdate, ContactResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get(
    '/',
    description='No more than 10 requests per minute',
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def get_all_contacts(
        offset: int = 0,
        limit: int = 50,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_postgres_db)
) -> list[ContactModel]:
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param offset: The number of contacts to skip.
    :type offset: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param current_user: The user to retrieve contacts for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts for the current user.
    :rtype: list[ContactModel]
    """
    contacts = await repository_contacts.get_all_contacts(offset, limit, current_user, db)

    return contacts


@router.get('/{contact_id}')
async def get_contact(
        contact_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_postgres_db)
) -> ContactResponse:
    """
    Retrieve a specific contact for the current user by contact ID.

    :param contact_id: The ID of the contact to retrieve. Must be greater than or equal to 1.
    :type contact_id: int
    :param current_user: The user to retrieve contact for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The retrieved contact details.
    :rtype: ContactResponse
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact is not found')

    return contact


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    description='No more than 10 requests per minute',
    dependencies=[Depends(RateLimiter(times=5, seconds=60))]
)
async def create_contact(
        body: ContactCreate,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_postgres_db)
) -> ContactResponse:
    """
    Create a new contact for the current user.

    :param body: The data schema for creating a new contact.
    :type body: ContactCreate
    :param current_user: The user to create contact for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact details.
    :rtype: ContactResponse
    """
    return await repository_contacts.create_contact(body, current_user, db)


@router.put('/{contact_id}')
async def update_contact(
        contact_id: int,
        body: ContactUpdate,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_postgres_db)
) -> ContactResponse:
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The data schema containing the updated contact information.
    :type body: ContactResponse
    :param current_user: The user to update contact for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact details.
    :rtype: ContactResponse
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact is not found')

    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
        contact_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_postgres_db)
):
    """
    Delete a contact for the current user by contact ID.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param current_user: The user to delete contact for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The removed contact, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact is not found')

    return contact


@router.get('/search_by_first_name/')
async def get_contact_by_first_name(
        contact_first_name: str = Query(),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_postgres_db)
) -> ContactResponse:
    """
    Retrieve a contact for the current user by their first name.

    :param contact_first_name: The first name of the contact to search for.
    :type contact_first_name: str
    :param current_user: The user to retrieve contact by contact's first name for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The retrieved contact details.
    :rtype: ContactResponse
    """
    contact = await repository_contacts.get_contact_by_first_name(contact_first_name, current_user, db)

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact is not found')

    return contact


@router.get('/search_by_last_name/')
async def get_contact_by_last_name(
        contact_last_name: str = Query(),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_postgres_db)
) -> ContactResponse:
    """
    Retrieve a contact for the current user by their last name.

    :param contact_last_name: The last name of the contact to search for.
    :type contact_last_name: str
    :param current_user: The user to retrieve contact by contact's last name for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The retrieved contact details.
    :rtype: ContactResponse
    """
    contact = await repository_contacts.get_contact_by_last_name(contact_last_name, current_user, db)

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact is not found')

    return contact


@router.get('/search_by_email/')
async def get_contact_by_email(
        contact_email: str = Query(),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_postgres_db)
) -> ContactResponse:
    """
    Retrieve a contact for the current user by their email address.

    :param contact_email: The email address of the contact to search for.
    :type contact_email: str
    :param current_user: The user to retrieve contact by contact's email for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The retrieved contact details.
    :rtype: ContactResponse
    """
    contact = await repository_contacts.get_contact_by_email(contact_email, current_user, db)

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact is not found')

    return contact


@router.get('/upcoming_birthdays/')
async def get_contacts_upcoming_birthdays(
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_postgres_db)
):
    """
    Retrieve contacts with upcoming birthdays for the current user.

    :param current_user: The user to retrieve contacts upcoming birthdays for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts with upcoming birthdays.
    :rtype: list[Contact]
    """
    contacts = await repository_contacts.get_contacts_upcoming_birthdays(current_user, db)

    return contacts
