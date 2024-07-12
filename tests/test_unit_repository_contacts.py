from datetime import datetime, timedelta
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.repository.contacts import (get_all_contacts, get_contact, create_contact, delete_contact, update_contact,
                                     get_contact_by_first_name, get_contact_by_last_name, get_contact_by_email,
                                     get_contacts_upcoming_birthdays)
from src.schemas.contacts import ContactUpdate, ContactCreate


class TestContacts(IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_all_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_all_contacts(offset=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactCreate(
            first_name='Test first name',
            last_name='Test last name',
            email='test@test',
            phone_number='test',
            birthday_date='2000-06-04'
        )
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday_date, body.birthday_date)
        self.assertTrue(hasattr(result, 'id'))

    async def test_delete_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactUpdate(
            first_name='Test first name',
            last_name='Test last name',
            email='test@test',
            phone_number='test',
            birthday_date='2000-06-04'
        )
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactUpdate(
            first_name='Test first name',
            last_name='Test last name',
            email='test@test',
            phone_number='test',
            birthday_date='2000-06-04'
        )
        self.session.query().filter().first.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contact_by_first_name_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_first_name(contact_first_name='Test', user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_first_name_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact_by_first_name(contact_first_name='Test', user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contact_by_last_name_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_last_name(contact_last_name='Test', user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_last_name_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact_by_last_name(contact_last_name='Test', user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contact_by_email_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_email(contact_email='test@test', user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact_by_email(contact_email='test@test', user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contacts_upcoming_birthdays_no_contacts(self):
        self.session.query().filter().all.return_value = []
        result = await get_contacts_upcoming_birthdays(user=self.user, db=self.session)
        self.assertEqual(result, [])

    async def test_get_contacts_upcoming_birthdays_with_contacts(self):
        date_today = datetime.today().date()
        contacts = [
            Contact(user_id=1, birthday_date=(date_today + timedelta(days=3)).strftime('%Y-%m-%d')),
            Contact(user_id=1, birthday_date=(date_today + timedelta(days=8)).strftime('%Y-%m-%d'))
        ]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts_upcoming_birthdays(user=self.user, db=self.session)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].birthday_date, (date_today + timedelta(days=3)).strftime('%Y-%m-%d'))

    async def test_get_contacts_upcoming_birthdays_no_upcoming_birthdays(self):
        date_today = datetime.today().date()
        contacts = [
            Contact(user_id=1, birthday_date=(date_today + timedelta(days=10)).strftime('%Y-%m-%d')),
            Contact(user_id=1, birthday_date=(date_today + timedelta(days=15)).strftime('%Y-%m-%d'))
        ]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts_upcoming_birthdays(user=self.user, db=self.session)
        self.assertEqual(result, [])

    async def test_get_contacts_upcoming_birthdays_edge_case_seventh_day(self):
        date_today = datetime.today().date()
        contacts = [
            Contact(user_id=1, birthday_date=(date_today + timedelta(days=7)).strftime('%Y-%m-%d'))
        ]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts_upcoming_birthdays(user=self.user, db=self.session)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].birthday_date, (date_today + timedelta(days=7)).strftime('%Y-%m-%d'))
