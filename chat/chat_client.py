"""The Python implementation of the gRPC chat client."""
import argparse
import time

import grpc

import chat_pb2
import chat_pb2_grpc


def create_parser():
    """Creates parser and returns argument 'action' from choices 
    or None if nothing was given.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Chat client provides such options:
                u    - get list of all users,
                m    - send message for another user,
                s    - make a subscription.''')
    parser.add_argument("-a", "--action", choices=['u', 'm', 's'],
                        help="u - get users, m - send message, s - subscribe")
    args = parser.parse_args()
    return args.action


def choose_option(choice, stub):
    """Invokes one of the functions depending on the selected option."""
    if choice == "u":
        get_users_list(stub)
    elif choice == "m":
        global login_from, login_to, body
        login_from = input("Input login from: ")
        login_to = input("Input login to: ")
        body = input("Input content: ")
        send_message(stub)
    elif choice == "s":
        global login
        login = input("Input login: ")
        subscribe(stub)
    else:
        print("Please, choose option. Use -h or --help for details.")


def get_users_list(stub):
    """Gets list of users."""
    users_list = stub.GetUsers(chat_pb2.GetUsersRequest())
    print(users_list.users)


def send_message(stub):
    """Sends message contained sender's login,
    recipient's login, creation timestamp and body-content.
    """
    message = chat_pb2.Message(login_from=login_from,
                               login_to=login_to,
                               created_at=int(time.time()),
                               body=body)
    response = stub.SendMessage(chat_pb2.SendMessageRequest(message=message))
    print(response.status)


def subscribe(stub):
    """Gets and prints all messages, given in stream."""
    messages = stub.Subscribe(chat_pb2.SubscribeRequest(login=login))
    for message in messages:
        print(message)


def run():
    """Creates and runs channel."""
    with grpc.insecure_channel('[::]:50051') as channel:
        stub = chat_pb2_grpc.ChatStub(channel)
        option = create_parser()
        choose_option(option, stub)


if __name__ == '__main__':
    run()
