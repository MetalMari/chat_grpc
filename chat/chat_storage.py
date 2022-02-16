"""The Python implementation of the etcd chat client."""

import json
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field, fields
from typing import List

import etcd3


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
    def __init__(self):
        """Initializes Storage object."""

    @abstractmethod
    def create_user(self, user: User) -> None:
        """Saves users in storage."""

    @abstractmethod
    def get_users_list(self) -> List[User]:
        """Returns users list from storage."""

    @abstractmethod
    def create_message(self, message: Message) -> None:
        """Saves messages in storage."""

    @abstractmethod
    def get_user_messages(self, login: str) -> List[Message]:
        """Returns list of messages from storage."""

    @abstractmethod
    def delete_user_message(self, message) -> None:
        """Deletes user-read messages."""


class EtcdStorage(Storage):
    """Provides methods for creating users, getting all users, 
    creating messages, getting all messages per user, removing specific
    message for specific user.
    """

    user_prefix = "user."
    message_prefix = "message."

    def __init__(self):
        """Initializes storage client via etcd."""
        self.client = etcd3.client()

    def create_user(self, user: User) -> None:
        """Saves user object into etcd using user key."""
        user_key = user.get_unique_key()
        user_value = json.dumps(asdict(user))
        self.client.put(user_key, user_value)

    def get_users_list(self) -> List[User]:
        """Returns list of users."""
        users = []
        for value, key in self.client.get_prefix(self.user_prefix):
            user = json.loads(value.decode())
            users.append(User(**user))
        return users

    def create_message(self, message: Message) -> None:
        """Saves message object into etcd using message key.
        Message key includes user login and timestamp created_at to be unique.
        """
        message_key = message.get_unique_key()
        message_value = json.dumps(asdict(message))
        self.client.put(message_key, message_value)

    def get_user_messages(self, login: str) -> List[Message]:
        """Returns list of messages for specific user."""
        messages = []
        message_key = self.message_prefix + login
        messages_from_db = self.client.get_prefix(message_key)
        for value, key in messages_from_db:
            message = json.loads(value.decode())
            messages.append(Message(**message))
        return messages

    def delete_user_message(self, message) -> None:
        """Deletes message from storage after sending it for user."""
        self.client.delete(message.get_unique_key())
