from datetime import datetime, timedelta

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas.contacts import ContactCreate, ContactUpdate


async def get_all_contacts(offset: int, limit: int, user: User, db: Session) -> list[Contact]:
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param offset: The number of contacts to skip.
    :type offset: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: list[Contact]
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(offset).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified ID, or None if it does not exist.
    :rtype: Note | None
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactCreate, user: User, db: Session) -> Contact:
    """
    Creates a new contact for a specific user.

    :param body: The data for the contact to create.
    :type body: ContactCreate
    :param user: The user to create the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contact
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactUpdate
    :param user: The user to update the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()

    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday_date = body.birthday_date

        db.commit()
        db.refresh(contact)

    return contact


async def delete_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Removes a single note with the specified ID for a specific user.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param user: The user to remove the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The removed contact, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()

    if contact:
        db.delete(contact)
        db.commit()

    return contact


async def get_contact_by_first_name(contact_first_name: str, user: User, db: Session) -> Contact | None:
    """
    Retrieves a single contact with the specified first name for a specific user.

    :param contact_first_name: The first name of the contact to retrieve.
    :type contact_first_name: str
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified first name, or None if it does not exist.
    :rtype: Contact | None
    """
    return db.query(Contact).filter(
        and_(Contact.user_id == user.id,
             func.lower(Contact.first_name) == contact_first_name.lower())
    ).first()


async def get_contact_by_last_name(contact_last_name: str, user: User, db: Session) -> Contact | None:
    """
    Retrieves a single contact with the specified last name for a specific user.

    :param contact_last_name: The last name of the contact to retrieve.
    :type contact_last_name: str
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified last name, or None if it does not exist.
    :rtype: Contact | None
    """
    return db.query(Contact).filter(
        and_(Contact.user_id == user.id,
             func.lower(Contact.last_name) == contact_last_name.lower())
    ).first()


async def get_contact_by_email(contact_email: str, user: User, db: Session) -> Contact | None:
    """
    Retrieves a single contact with the specified email for a specific user.

    :param contact_email: The email of the contact to retrieve.
    :type contact_email: str
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified email, or None if it does not exist.
    :rtype: Contact | None
    """
    return db.query(Contact).filter(
        and_(Contact.user_id == user.id,
             Contact.email == contact_email)
    ).first()


async def get_contacts_upcoming_birthdays(user: User, db: Session) -> list[Contact]:
    """
    Retrieves a list of contacts of a user who have birthdays within the next 7 days.

    :param user: The user to retrieve the contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts with upcoming birthdays within the next 7 days.
    :rtype: list[Contact]
    """
    contacts_upcoming_birthdays = []
    date_today = datetime.today().date()
    today_plus_week = date_today + timedelta(days=7)

    contacts = db.query(Contact).filter(Contact.user_id == user.id).all()

    for contact in contacts:
        birthday = datetime.strptime(str(contact.birthday_date), '%Y-%m-%d').date().replace(year=date_today.year)

        if date_today.timetuple().tm_yday <= birthday.timetuple().tm_yday <= today_plus_week.timetuple().tm_yday:
            contacts_upcoming_birthdays.append(contact)

    return contacts_upcoming_birthdays
