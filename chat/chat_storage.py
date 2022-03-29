"""The Python implementation of the etcd chat client."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


USER_PREFIX = "user."
MESSAGE_PREFIX = "message."


@dataclass
class User:

    """Class for user entity."""

    login: str
    full_name: str

    def get_unique_key(self):
        """Creates unique key for saving user."""
        return "user.{}".format(self.login)


@dataclass
class Message:

    """Class for message entity."""

    login_from: str
    login_to: str
    body: str
    created_at: int = field(default_factory=lambda: int(time.time()))

    def get_unique_key(self):
        """Creates unique key for saving message."""
        return "message.{}.{}.{}".format(self.login_to, self.login_from,
                                         self.created_at)


class Storage(ABC):

    """Base class for creating storages.All subclasses need to provide methods 
    for initializing storage, creating users, getting all users, creating messages, 
    getting all messages per user, removing specific message for specific user.
    """

    @abstractmethod
    def __init__(self, host, port):
        """Initializes Storage object."""
        pass

    @abstractmethod
    def create_user(self, user: User):
        """Saves users in storage."""
        pass

    @abstractmethod
    def get_users_list(self) -> List[User]:
        """Returns users list from storage."""
        pass

    @abstractmethod
    def create_message(self, message: Message):
        """Saves messages in storage."""
        pass

    @abstractmethod
    def get_user_messages(self, login: str) -> List[Message]:
        """Returns list of messages from storage."""
        pass

    @abstractmethod
    def delete_user_message(self, message: Message):
        """Deletes user-read messages."""
        pass


class UnknownStorageError(Exception):

    """Exception raised if unknown storage name is used."""

    pass


class StorageFactory:

    """The StorageFactory class declares the create_storage method 
    that is supposed to return an object of a Storage class.
    """

    @classmethod
    def storage_register(cls, **storage_data):
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
