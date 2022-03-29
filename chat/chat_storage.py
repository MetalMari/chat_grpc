"""The Python implementation of the etcd chat client."""

import json
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field, fields
from typing import List

import etcd3


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


class EtcdStorage(Storage):

    """Provides methods for creating users, getting all users, 
    creating messages, getting all messages per user, removing specific
    message for specific user.
    """

    def __init__(self, host, port):
        """Initializes storage client via etcd."""
        self.client = etcd3.client(host=host, port=port)

    def create_user(self, user: User):
        """Saves user object into etcd using user key."""
        user_key = user.get_unique_key()
        user_value = json.dumps(asdict(user))
        self.client.put(user_key, user_value)

    def get_users_list(self) -> List[User]:
        """Returns list of users."""
        users = []
        for value, key in self.client.get_prefix(USER_PREFIX):
            user = json.loads(value.decode())
            users.append(User(**user))
        return users

    def create_message(self, message: Message):
        """Saves message object into etcd using message key.
        Message key includes user login and timestamp created_at to be unique.
        """
        message_key = message.get_unique_key()
        message_value = json.dumps(asdict(message))
        self.client.put(message_key, message_value)

    def get_user_messages(self, login: str) -> List[Message]:
        """Returns list of messages for specific user."""
        messages = []
        message_key = "{}{}.".format(MESSAGE_PREFIX, login)
        messages_from_db = self.client.get_prefix(message_key)
        for value, key in messages_from_db:
            message = json.loads(value.decode())
            messages.append(Message(**message))
        return messages

    def delete_user_message(self, message: Message):
        """Deletes message from storage after sending it for user."""
        self.client.delete(message.get_unique_key())


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


StorageFactory.storage_register(etcd = EtcdStorage)
