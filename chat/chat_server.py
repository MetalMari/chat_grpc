"""The Python implementation of the gRPC chat server."""

import logging
import os
import time
from concurrent import futures

import grpc

import sys

import chat_pb2
import chat_pb2_grpc
from chat_storage import Message, Storage, User, StorageFactory, UnknownStorageError


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
        self.storage.create_message(Message(request.message.login_from,
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


def create_users_list(storage: Storage):
    """Creates users and saves them to storage."""
    user_list = [User(f"user_{x}", f"{x}"*2 + ' ' + f"{x}"*3)
                 for x in "ABCD"]
    for user in user_list:
        storage.create_user(user)


def create_server(storage: Storage, server_host: str, server_port: str):
    """Creates server on defined address and port."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    if not storage.get_users_list():
        create_users_list(storage)
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(storage), server)
    server.add_insecure_port("{}:{}".format(server_host, server_port))
    return server


def main():
    """Gets environment variables, initializes storage and server. 
    Starts the server.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("config_logger")
    storage_type = os.environ.get("STORAGE")
    storage_host = os.environ.get("STORAGE_HOST")
    storage_port = os.environ.get("STORAGE_PORT")
    server_host = os.environ.get("SERVER_HOST")
    server_port = os.environ.get("SERVER_PORT")
    try:
        storage = StorageFactory.create_storage(
            storage_type, storage_host, storage_port)
    except UnknownStorageError as error:
        logger.error(f"{error}. Please, check config file if STORAGE name \
is entered and correct.")
        sys.exit(1)
    server = create_server(storage, server_host, server_port)
    server.start()
    logging.info('Starting server..')
    server.wait_for_termination()


if __name__ == '__main__':
    main()
