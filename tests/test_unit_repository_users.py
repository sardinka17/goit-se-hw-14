import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.users import (get_user_by_email, update_avatar, confirmed_email, update_token)


class TestUsers(IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email_found(self):
        email = 'test@example.com'
        user = User(id=1, email=email)
        self.session.query().filter().first.return_value = user

        result = await get_user_by_email(email=email, db=self.session)

        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None

        result = await get_user_by_email(email='test@example.com', db=self.session)

        self.assertIsNone(result)

    async def test_update_token(self):
        user = User(id=1, email='test@example.com')
        token = 'new_token'

        await update_token(user=user, token=token, db=self.session)

        self.assertEqual(user.refresh_token, token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        email = 'test@example.com'
        user = User(id=1, email=email, confirmed=False)
        self.session.query().filter().first = MagicMock(return_value=user)
        mock_get_user_by_email = AsyncMock(return_value=user)

        with unittest.mock.patch('src.repository.users.get_user_by_email', mock_get_user_by_email):
            await confirmed_email(email=email, db=self.session)

        self.assertTrue(user.confirmed)
        self.session.commit.assert_called_once()

    async def test_update_avatar(self):
        email = 'test@example.com'
        user = User(id=1, email=email, avatar='old_url')
        new_url = 'new_avatar_url'
        self.session.query().filter().first = MagicMock(return_value=user)
        mock_get_user_by_email = AsyncMock(return_value=user)

        with unittest.mock.patch('src.repository.users.get_user_by_email', mock_get_user_by_email):
            updated_user = await update_avatar(email=email, url=new_url, db=self.session)

        self.assertEqual(updated_user.avatar, new_url)
        self.session.commit.assert_called_once()
