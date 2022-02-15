"""The Python implementation of the etcd chat client."""

import json
from abc import ABC, abstractmethod
from typing import List

import etcd3

from chat_server import Message, User


class Storage(ABC):
    """Base class for creating storages.All subclasses need to provide methods 
    for initializing storage, creating users, getting all users, creating messages, 
    getting all messages per user, removing specific message for specific user.
    """

    @abstractmethod
    def __init__(self):
        """Initializes Storage object."""

    @abstractmethod
    def create_user(self, user) -> None:
        """Saves users in storage."""

    @abstractmethod
    def get_users_list(self) -> List[User]:
        """Returns users list from storage."""

    @abstractmethod
    def create_message(self, message) -> None:
        """Saves messages in storage."""

    @abstractmethod
    def get_user_messages(self, login) -> List[Message]:
        """Returns list of messages from storage."""

    @abstractmethod
    def delete_user_message(self, login, created_at) -> None:
        """Deletes user-read messages."""


class EtcdStorage(Storage):
    """Provides methods for creating users, getting all users, 
    creating messages, getting all messages per user, removing specific
    message for specific user.
    """

    def __init__(self):
        """Initializes storage client via etcd."""
        self.client = etcd3.client()
        self.user_prefix = "user."
        self.message_prefix = "message."

    def create_user(self, user) -> None:
        """Saves user object into etcd using user key."""
        user_key = self.user_prefix + user.login
        user_to_json = user.to_dict()
        user_value = json.dumps(user_to_json)
        self.client.put(user_key, user_value)

    def get_users_list(self) -> List[User]:
        """Returns list of users."""
        users = []
        for value, key in self.client.get_prefix(self.user_prefix):
            user = json.loads(value.decode('utf-8'))
            users.append(User(**user))
        return users

    def create_message(self, message) -> None:
        """Saves message object into etcd using message key.
        Message key includes user login and timestamp created_at to be unique.
        """
        message_key = self.message_prefix + \
            message.login_to + str(message.created_at)
        message_to_json = message.to_dict()
        message_value = json.dumps(message_to_json)
        self.client.put(message_key, message_value)

    def get_user_messages(self, login) -> List[Message]:
        """Returns list of messages for specific user."""
        messages = []
        message_key = self.message_prefix + login
        messages_from_db = self.client.get_prefix(message_key)
        for value, key in messages_from_db:
            message = json.loads(value.decode('utf-8'))
            messages.append(Message(**message))
        return messages

    def delete_user_message(self, login, created_at) -> None:
        """Deletes message from storage after sending it for user."""
        key_to_delete = self.message_prefix + login + str(created_at)
        self.client.delete(key_to_delete)
