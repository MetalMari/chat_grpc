"""The Python implementation of the gRPC chat server."""

import logging
import os
import time
from concurrent import futures

import grpc

import chat_pb2
import chat_pb2_grpc
import chat_storage


class Chat(chat_pb2_grpc.ChatServicer):
    """Provides methods that implement functionality of chat server."""

    def __init__(self, storage):
        self.storage = storage

    def GetUsers(self, request, context):
        """Returns list of users from storage."""
        users = []
        users_from_db = self.storage.get_users_list()
        for user in users_from_db:
            users.append(chat_pb2.User(
                login=user.login, full_name=user.full_name))
        return chat_pb2.GetUsersReply(users=users)

    def SendMessage(self, request, context):
        """Gets message and saves it to storage. 
        Returns simple string if the message from client is received.
        """
        self.storage.create_message(chat_storage.Message(request.message.login_from,
                                                         request.message.login_to,
                                                         request.message.body))
        return chat_pb2.SendMessageReply(
            status=f"Done! {request.message.login_to} received message " +
            f"from {request.message.login_from}!"
        )

    def Subscribe(self, request, context):
        """Returns stream of messages from storage by subscription."""
        while context.is_active():
            messages = self.storage.get_user_messages(request.login)
            for message in messages:
                yield chat_pb2.Message(login_from=message.login_from,
                                       login_to=message.login_to,
                                       created_at=message.created_at,
                                       body=message.body)
                self.storage.delete_user_message(message)
                time.sleep(5)


def create_users_list(storage):
    """Creates users and saves them to storage."""
    user_list = [chat_storage.User(f"user_{x}", f"{x}"*2 + ' ' + f"{x}"*3)
                 for x in "ABCD"]
    for user in user_list:
        storage.create_user(user)


def initialize_storage():
    """Choses strategy for storage initializing.
    Depends on environment variables.
    """
    if os.environ.get("STORAGE") == "etcd":
        return chat_storage.EtcdStorage()


def create_server():
    """Creates server on defined address and port."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    storage = initialize_storage()
    if os.environ.get("FILL_USERS") == "storage_users":
        create_users_list(storage)
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(storage), server)
    server.add_insecure_port("[::]:50051")
    return server


if __name__ == '__main__':
    logging.basicConfig()
    server = create_server()
    server.start()
    server.wait_for_termination()
