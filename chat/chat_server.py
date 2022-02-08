"""The Python implementation of the gRPC chat server."""

import time
from concurrent import futures

import grpc

import chat_pb2
import chat_pb2_grpc


class UsersList(chat_pb2_grpc.ChatServicer):
    """Provides methods that implement functionality of chat server."""

    def GetUsers(self, request, context):
        """Returns list of users."""
        user_list = [chat_pb2.User(login="user_a", full_name="James Hetfield"),
                     chat_pb2.User(login="user_b", full_name="Lars Ulrich"),
                     chat_pb2.User(login="user_c", full_name="Kirk Hammet"),
                     chat_pb2.User(login="user_d", full_name="Roberto Trujillo")]
        return chat_pb2.GetUsersReply(users=user_list)

    def SendMessage(self, request, context):
        """Returns simple string if the message from client is received."""
        return chat_pb2.SendMessageReply(
            status=f"Done! {request.login_to} received message from {request.login_from}!"
        )

    def Subscribe(self, request, context):
        """Returns stream of messages by subscription."""
        counter = 20  # random number for testing.
        while counter > 0:
            yield chat_pb2.Message(login_from="userA",
                                   login_to=request.login,
                                   created_at=int(time.time()),
                                   body="This is new message for you!")
            counter -= 1

    def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        chat_pb2_grpc.add_ChatServicer_to_server(
            chat_pb2_grpc.ChatServicer(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        server.wait_for_termination()

    if __name__ == '__main__':
        serve()
