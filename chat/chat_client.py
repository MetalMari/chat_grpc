"""The Python implementation of the gRPC chat client."""
import argparse
import time

import grpc

import chat_pb2
import chat_pb2_grpc


class IncorrectDataError(Exception):
    """Exception raised for errors in the input data.

    Attributes:
        message -- explanation of the error.
    """

    def __init__(self, message="Incorrect data."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


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
                        metavar=('sender', 'recipient', 'content'))
    parser.add_argument('-s', '--subscribe', action="store", metavar=('login'))
    return parser


def is_data_valid(args):
    """Checks if all data is available for sending a message or subscription."""
    if args.action == "users" and (args.message or args.subscribe):
        raise IncorrectDataError
    elif args.action == "message" and not args.message:
        raise IncorrectDataError
    elif args.action == "subscribe" and not args.subscribe:
        raise IncorrectDataError
    return True


def choose_action(args, stub):
    """Invokes one of the functions depending on the selected option."""
    if args.action == "users":
        get_users_list(stub)
    elif args.action == "message":
        send_message(stub, *args.message)
    else:
        subscribe(stub, args.subscribe)


def get_users_list(stub):
    """Gets list of users."""
    users_list = stub.GetUsers(chat_pb2.GetUsersRequest())
    print(users_list.users)


def send_message(stub, login_from, login_to, body):
    """Sends message contained sender's login,
    recipient's login, creation timestamp and body-content.
    """
    message = chat_pb2.Message(login_from=login_from,
                               login_to=login_to,
                               created_at=int(time.time()),
                               body=body)
    response = stub.SendMessage(chat_pb2.SendMessageRequest(message=message))
    print(response.status)


def subscribe(stub, login):
    """Gets and prints all messages, given in stream."""
    messages = stub.Subscribe(chat_pb2.SubscribeRequest(login=login))
    for message in messages:
        print(message)


def run():
    """Creates and runs channel."""
    parser = create_parser()
    args = parser.parse_args()
    try:
        is_data_valid(args)
    except IncorrectDataError as error:
        print(error)
    else:
        with grpc.insecure_channel('[::]:50051') as channel:
            stub = chat_pb2_grpc.ChatStub(channel)
            choose_action(args, stub)


if __name__ == '__main__':
    run()
