from datetime import datetime, timedelta

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas.contacts import ContactCreate, ContactUpdate


async def get_all_contacts(offset: int, limit: int, user: User, db: Session) -> list[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(offset).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactCreate, user: User, db: Session) -> Contact:
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
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
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()

    if contact:
        db.delete(contact)
        db.commit()

    return contact


async def get_contact_by_first_name(contact_first_name: str, user: User, db: Session) -> Contact | None:
    return db.query(Contact).filter(
        and_(Contact.user_id == user.id,
             func.lower(Contact.first_name) == contact_first_name.lower())
    ).first()


async def get_contact_by_last_name(contact_last_name: str, user: User, db: Session) -> Contact | None:
    return db.query(Contact).filter(
        and_(Contact.user_id == user.id,
             func.lower(Contact.last_name) == contact_last_name.lower())
    ).first()


async def get_contact_by_email(contact_email: str, user: User, db: Session) -> Contact | None:
    return db.query(Contact).filter(
        and_(Contact.user_id == user.id,
             Contact.email == contact_email)
    ).first()


async def get_contacts_upcoming_birthdays(user: User, db: Session):
    contacts_upcoming_birthdays = []
    date_today = datetime.today().date()
    today_plus_week = date_today + timedelta(days=7)

    contacts = db.query(Contact).filter(Contact.user_id == user.id).all()

    for contact in contacts:
        birthday = datetime.strptime(str(contact.birthday_date), '%Y-%m-%d').date().replace(year=date_today.year)

        if date_today.timetuple().tm_yday <= birthday.timetuple().tm_yday <= today_plus_week.timetuple().tm_yday:
            contacts_upcoming_birthdays.append(contact)

    return contacts_upcoming_birthdays
