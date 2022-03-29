"""This module contains StorageFactory supposed to register 
new storage types and to create new storage instances if
they are already registered.
"""

from storages.etcd_storage import EtcdStorage


class UnknownStorageError(Exception):

    """Exception raised if unknown storage name is used."""

    pass


class StorageFactory:

    """StorageFactory class provides methods for adding new 
    storage types and initializing an object of a Storage class.
    """

    @classmethod
    def register_storage(cls, **storage_data):
        """Registers Storage subclass as StorageFactory attribute."""
        for key in storage_data:
            setattr(cls, key, storage_data[key])

    @staticmethod
    def create_storage(storage_type: str, host: str, port: str):
        """Returns storage object according to storage type."""
        try:
            return StorageFactory.__dict__[storage_type](host, port)
        except KeyError:
            raise UnknownStorageError(f"Unknown storage type: {storage_type}")


StorageFactory.register_storage(etcd=EtcdStorage)
