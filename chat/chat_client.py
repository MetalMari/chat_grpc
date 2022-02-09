"""The Python implementation of the gRPC chat client."""

from __future__ import print_function

import logging
import time

import grpc

import chat_pb2
import chat_pb2_grpc


def get_users_list(stub):
    """Gets list of users."""
    users_list = stub.GetUsers(chat_pb2.GetUsersRequest())
    print(users_list.users)


def send_message(stub):
    """Sends message contained sender's login,
    recipient's login, creation timestamp and body-content.
    """
    message = chat_pb2.Message(login_from="user_Sender",
                               login_to="user_Recipient",
                               created_at=int(time.time()),
                               body="First message.")
    response = stub.SendMessage(chat_pb2.SendMessageRequest(message=message))
    print(response.status)


def subscribe(stub):
    """Gets and prints all messages, given in stream."""
    messages = stub.Subscribe(chat_pb2.SubscribeRequest(login="New_user"))
    for message in messages:
        print(message)


def run():
    """Creates and runs channel."""
    with grpc.insecure_channel('[::]:50051') as channel:
        stub = chat_pb2_grpc.ChatStub(channel)
        print("-------------- GetUsersList --------------")
        get_users_list(stub)
        print("-------------- SendMessage ---------------")
        send_message(stub)
        print("-------------- Subscribe -----------------")
        subscribe(stub)


if __name__ == '__main__':
    logging.basicConfig()
    run()
