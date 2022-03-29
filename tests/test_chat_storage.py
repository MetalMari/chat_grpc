"""Python module for testing chat_storage module."""

from curses.ascii import ETB
from unittest import TestCase, mock

from chat_storage import Message, User
from storages.etcd_storage import EtcdStorage
from chat_storage_factory import StorageFactory, UnknownStorageError


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


class TestStorageFactory(TestCase):

    """Tests StorageFactory class."""

    def test_register_storage(self):
        """Tests 'register_storage' method."""
        StorageFactory.register_storage(db="mongo")
        self.assertTrue("db" in StorageFactory.__dict__.keys())
        self.assertEqual("mongo", StorageFactory.__dict__["db"])

    def test_create_storage(self):
        """Tests 'create_storage' method."""
        storage = StorageFactory.create_storage(
            "etcd", 'localhost', 2379)
        self.assertIsInstance(storage, EtcdStorage)

    def test_storage_type_valid_or_raiserror(self):
        """Tests 'create_storage' method and check raiserror."""
        with self.assertRaises(UnknownStorageError) as err:
            StorageFactory.create_storage(
                "etty", 'local', 2379)
        expected = "Unknown storage type: etty"
        self.assertEqual(str(err.exception), expected)
