"""Python module for testing chat_storage module."""

from unittest import TestCase

from chat_storage import Message, User


class TestUserInstance(TestCase):
    """Tests User class."""

    def setUp(self):
        """Creates user data to be used by the tests."""
        self.user_data = {"login": 'user1', "full_name": "AA AAA"}

    def test_get_unique_key(self):
        """Tests get unique key method."""
        user = User(**self.user_data)
        key = user.get_unique_key()
        expected_key = "user.user1"
        self.assertEqual(expected_key, key)


class TestMessageInstance(TestCase):
    """Tests Message class."""

    def setUp(self):
        """Creates message data to be used by the tests."""
        self.message_data = {"login_from": "user1", "login_to": "user2",
                             "body": "Hello, you!", "created_at": 1234}

    def test_get_unique_key(self):
        """Tests get unique key method."""
        user = Message(**self.message_data)
        key = user.get_unique_key()
        expected_key = "message.user2.user1.1234"
        self.assertEqual(expected_key, key)
