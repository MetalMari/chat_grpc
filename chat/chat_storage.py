"""This module contains implementation of basic Storage class, 
interface declares a set of methods for different storage types.
Also User and Message entities are using for server-storage interaction.
"""

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
