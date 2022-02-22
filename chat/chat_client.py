"""The Python implementation of the gRPC chat client."""

import argparse
import time

import grpc

import chat_pb2
import chat_pb2_grpc


class IncorrectDataError(Exception):
    """Exception raised for errors in the input data."""


def create_parser():
    """Creates parser and return parser with required argument 'action' from
    choices and optional data for sending message or subscription.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Chat client provides such options:
                users        - get list of all users,
                message      - send message for another user,
                subscribe    - make a subscription.''')
    parser.add_argument("action", choices=["users", "message", "subscribe"],
                        help="get users, send message, to subscribe.")
    parser.add_argument('-m', '--message', nargs=3,
                        metavar=('login_from', 'login_to', 'text_body'))
    parser.add_argument('-s', '--subscribe', metavar=('login'))
    parser.add_argument('-host', '--host', default='localhost',
                        help="define host for connection.")
    parser.add_argument('-p', '--port', default=50051,
                        help="define port for connection.")
    return parser


def message_data_valid_or_raiserror(args):
    """Checks if all data is available for sending a message."""
    if not args.message:
        raise IncorrectDataError(
            "Incorrect data. Please, check action or data.")


def subscribe_data_valid_or_raiserror(args):
    """Checks if all data is available for subscription."""
    if not args.subscribe:
        raise IncorrectDataError(
            "Incorrect data. Please, check action or data.")


def choose_action(args, stub):
    """Invokes one of the functions depending on the selected option."""
    if args.action == "users":
        get_users_list(stub)
    elif args.action == "message":
        send_message(args, stub)
    else:
        subscribe(args, stub)


def get_users_list(stub):
    """Gets list of users if data from client is correct."""
    users_list = stub.GetUsers(chat_pb2.GetUsersRequest())
    print(users_list.users)


def send_message(args, stub):
    """Sends message contained sender's login,
    recipient's login, creation timestamp and body-content
    if data from client is correct.
    """
    message_data_valid_or_raiserror(args)
    login_from = args.message[0]
    login_to = args.message[1]
    body = args.message[2]
    message = chat_pb2.Message(login_from=login_from,
                               login_to=login_to,
                               body=body)
    response = stub.SendMessage(
        chat_pb2.SendMessageRequest(message=message))
    print(response.status)


def subscribe(args, stub):
    """Gets and prints all messages, given in stream 
    if data from client is correct.
    """
    subscribe_data_valid_or_raiserror(args)
    login = args.subscribe
    messages = stub.Subscribe(chat_pb2.SubscribeRequest(login=login))
    for message in messages:
        print(message)


def run():
    """Creates and runs channel."""
    parser = create_parser()
    args = parser.parse_args()
    address = "{}:{}".format(args.host, args.port)
    with grpc.insecure_channel(address) as channel:
        stub = chat_pb2_grpc.ChatStub(channel)
        choose_action(args, stub)


if __name__ == '__main__':
    run()
