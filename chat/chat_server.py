"""The Python implementation of the gRPC chat server."""

import logging
from concurrent import futures
from dataclasses import dataclass, fields

import grpc

import chat_pb2
import chat_pb2_grpc
import etcd_client


@dataclass
class User:
    """Class for user objects. Designed to simplify work with the storage."""
    login: str
    full_name: str

    def to_dict(self):
        return dict((field.name, getattr(self, field.name)) for field in fields(self))


@dataclass
class Message:
    """Class for message objects. Designed to simplify work with the storage."""
    login_from: str
    login_to: str
    created_at: int
    body: str

    def to_dict(self):
        return dict((field.name, getattr(self, field.name)) for field in fields(self))


class Chat(chat_pb2_grpc.ChatServicer):
    """Provides methods that implement functionality of chat server."""

    def __init__(self):
        self.db = etcd_client.EtcdStorage()

    def GetUsers(self, request, context):
        """Returns list of users from storage."""
        users = []
        user_list = [User(f"user_{x}", f"{x}"*2 + ' ' + f"{x}"*3) for x in 'ABCD']
        for user in user_list:
            self.db.create_user(user)
        users_list_from_db = self.db.get_users_list()
        for user in users_list_from_db:
            users.append(chat_pb2.User(login=user.login, full_name=user.full_name))
        return chat_pb2.GetUsersReply(users=users)

    def SendMessage(self, request, context):
        """Gets message and saves it to storage. 
        Returns simple string if the message from client is received.
        """
        login_from = request.message.login_from
        login_to = request.message.login_to
        created_at = request.message.created_at
        body = request.message.body
        message_to_save = Message(login_from, login_to, created_at, body)
        self.db.create_message(message_to_save)
        return chat_pb2.SendMessageReply(
            status=f"Done! {login_to} received message " +
            f"from {login_from}!"
        )

    def Subscribe(self, request, context):
        """Returns stream of messages from storage by subscription."""
        login = request.login
        messages = self.db.get_user_messages(login)
        for message in messages:
            yield chat_pb2.Message(login_from=message.login_from,
                                   login_to=message.login_to,
                                   created_at=message.created_at,
                                   body=message.body)
            self.db.delete_user_message(message.login_to, message.created_at)


def create_server():
    """Creates server on defined address and port."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
    server.add_insecure_port('[::]:50051')
    return server


if __name__ == '__main__':
    logging.basicConfig()
    server = create_server()
    server.start()
    server.wait_for_termination()
