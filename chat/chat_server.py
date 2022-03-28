"""The Python implementation of the gRPC chat server."""

import logging
import os
import sys
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
                time.sleep(1)


class StorageFactory:

    """The StorageFactory class declares the create_storage method 
    that is supposed to return an object of a Storage class.
    """

    @staticmethod
    def create_storage(storage_type, host, port):
        """Returns storage object according to storage type."""
        storage_dict = {"etcd": chat_storage.EtcdStorage}
        try:
            return storage_dict[storage_type](host, port)
        except KeyError:
            logging.error("Unknown STORAGE name. Please, check if storage \
name is entered and correct.", exc_info=True)
            sys.exit(1)


def create_users_list(storage):
    """Creates users and saves them to storage."""
    user_list = [chat_storage.User(f"user_{x}", f"{x}"*2 + ' ' + f"{x}"*3)
                 for x in "ABCD"]
    for user in user_list:
        storage.create_user(user)


def create_server(storage, server_host, server_port):
    """Creates server on defined address and port."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    if not storage.get_users_list():
        create_users_list(storage)
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(storage), server)
    server.add_insecure_port("{}:{}".format(server_host, server_port))
    return server


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    storage_type = os.environ.get("STORAGE")
    storage_host = os.environ.get("STORAGE_HOST")
    storage_port = os.environ.get("STORAGE_PORT")
    server_host = os.environ.get("SERVER_HOST")
    server_port = os.environ.get("SERVER_PORT")
    storage = StorageFactory.create_storage(
        storage_type, storage_host, storage_port)
    server = create_server(storage, server_host, server_port)
    server.start()
    logging.info('Starting server..')
    server.wait_for_termination()
