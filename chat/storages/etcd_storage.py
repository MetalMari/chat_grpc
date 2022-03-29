import json
from dataclasses import asdict
from typing import List

import etcd3
from chat_storage import Message, Storage, StorageFactory, User

USER_PREFIX = "user."
MESSAGE_PREFIX = "message."


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


StorageFactory.register_storage(etcd=EtcdStorage) # add EtcdStorage to storage register
