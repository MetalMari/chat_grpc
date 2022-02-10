"""The Python implementation of the gRPC chat client."""
import argparse
import time

import grpc

import chat_pb2
import chat_pb2_grpc


class IncorrectDataError(Exception):
    """Exception raised for errors in the input data."""


def create_parser():
    """Creates parser and returns argument 'action' from choices 
    or None if nothing was given.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Chat client provides such options:
                users        - get list of all users,
                message      - send message for another user,
                subscribe    - make a subscription.''')
    parser.add_argument("action", choices=['users', 'message', 'subscribe'],
                        help="get users, send message, to subscribe.")
    parser.add_argument('-m', '--message', nargs=3,
                        metavar=('login_from', 'login_to', 'text_body'))
    parser.add_argument('-s', '--subscribe', metavar=('login'))
    return parser


def users_list_data_valid_or_raiserror(args):
    """Checks if there isn't unexpected data from user."""
    if args.message or args.subscribe:
        raise IncorrectDataError(
            "Unexpected data. Please, check action or data.")


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
        get_users_list(args, stub)
    elif args.action == "message":
        send_message(args, stub)
    else:
        subscribe(args, stub)


def get_users_list(args, stub):
    """Gets list of users."""
    try:
        users_list_data_valid_or_raiserror(args)
    except IncorrectDataError as error:
        print(error)
    else:
        users_list = stub.GetUsers(chat_pb2.GetUsersRequest())
        print(users_list.users)


def send_message(args, stub):
    """Sends message contained sender's login,
    recipient's login, creation timestamp and body-content.
    """
    try:
        message_data_valid_or_raiserror(args)
    except IncorrectDataError as error:
        print(error)
    else:
        login_from = args.message[0]
        login_to = args.message[1]
        body = args.message[2]
        message = chat_pb2.Message(login_from=login_from,
                                   login_to=login_to,
                                   created_at=int(time.time()),
                                   body=body)
        response = stub.SendMessage(
            chat_pb2.SendMessageRequest(message=message))
        print(response.status)


def subscribe(args, stub):
    """Gets and prints all messages, given in stream."""
    try:
        subscribe_data_valid_or_raiserror(args)
    except IncorrectDataError as error:
        print(error)
    else:
        login = args.subscribe
        messages = stub.Subscribe(chat_pb2.SubscribeRequest(login=login))
        for message in messages:
            print(message)


def run():
    """Creates and runs channel."""
    parser = create_parser()
    args = parser.parse_args()
    with grpc.insecure_channel('[::]:50051') as channel:
        stub = chat_pb2_grpc.ChatStub(channel)
        choose_action(args, stub)


if __name__ == '__main__':
    run()
