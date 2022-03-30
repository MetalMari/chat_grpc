"""Python module for testing chat_storage_factory module."""

from unittest import TestCase

from chat_storage_factory import StorageFactory, UnknownStorageError
from storages.etcd_storage import EtcdStorage


class TestStorageFactory(TestCase):

    """Tests StorageFactory class."""

    def test_register_storage(self):
        """Tests 'register_storage' method."""
        StorageFactory.register_storage("db", "mongo")
        self.assertTrue("db" in StorageFactory.storage_registry.keys())
        self.assertEqual("mongo", StorageFactory.storage_registry["db"])

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
