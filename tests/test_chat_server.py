"""Python module for testing 'chat_server' module."""

from unittest import mock, TestCase
from itertools import islice

import chat_pb2
from chat_storage import User, Message
from storages.etcd_storage import EtcdStorage
import chat_server


class TestChat(TestCase):

    """Tests Chat class."""

    @classmethod
    def setUpClass(cls):
        """Creates users to be used by the tests."""
        cls.user1 = User(login="userA", full_name="AA AAA")
        cls.user2 = User(login="userB", full_name="BB BBB")

    def setUp(self):
        """Creates storage and chat object to be used by the tests."""
        self.storage = mock.Mock()
        self.chat = chat_server.Chat(self.storage)

    def test_GetUsers(self):
        """Tests 'GetUsers' method."""
        self.storage.client.get_prefix.return_value = [self.user1, self.user2]
        self.storage.get_users_list.return_value = [self.user1, self.user2]
        users = [chat_pb2.User(login="userA", full_name="AA AAA"),
                 chat_pb2.User(login="userB", full_name="BB BBB")]
        expected = chat_pb2.GetUsersReply(users=users)
        result = self.chat.GetUsers(mock.Mock(), mock.Mock())
        self.assertEqual(expected, result)

    @mock.patch("chat_storage.time.time")
    def test_SendMessage(self, mock_time):
        """Tests 'SendMessage' method."""
        mock_time.return_value = 1111
        self.storage.create_message = mock.Mock()
        request = mock.Mock(message=mock.Mock(login_from="userA",
                                              login_to="userB",
                                              body="Hello, you."))
        expected = chat_pb2.SendMessageReply(
            status=f"Done! {request.message.login_to} received message " +
            f"from {request.message.login_from}!"
        )
        result = self.chat.SendMessage(request, mock.Mock())
        self.storage.create_message.assert_called_with(
            Message(request.message.login_from, request.message.login_to, request.message.body))
        self.assertEqual(expected, result)

    @mock.patch("chat_storage.time.sleep")
    def test_Subscribe(self, mock_time):
        """Tests 'Subscribe' method."""
        mock_time.return_value = None
        request = mock.Mock(login="B")
        context = mock.Mock()
        context.is_active.return_value = True
        self.storage.get_user_messages.return_value = [
            Message(login_from="A", login_to="B",
                    body="Hello, you!", created_at=1234),
            Message(login_from="C", login_to="B", body="Hello!", created_at=12345)]
        expected = [chat_pb2.Message(login_from="A",
                                     login_to="B",
                                     created_at=1234,
                                     body="Hello, you!"),
                    chat_pb2.Message(login_from="C",
                                     login_to="B",
                                     created_at=12345,
                                     body="Hello!")
                    ]
        result = [message for message in islice(
            self.chat.Subscribe(request, context), 0, 3)]
        calls = [mock.call(Message(login_from="A", login_to="B",
                                   body="Hello, you!", created_at=1234)),
                 mock.call(Message(login_from='C', login_to='B',
                                   body='Hello!', created_at=12345))]
        self.storage.get_user_messages.assert_called_with("B")
        self.storage.delete_user_message.assert_has_calls(calls)
        self.assertListEqual(expected, result[:2])


class TestServerFunctions(TestCase):

    """Class for testing chat_server functions."""

    def test_create_users_list(self):
        """Tests 'create_users_list' method."""
        self.storage = mock.Mock()
        self.storage.create_user = mock.Mock()
        chat_server.create_users_list(self.storage)
        calls = [mock.call(User(login='user_A', full_name='AA AAA')),
                 mock.call(User(login='user_B', full_name='BB BBB'))]
        self.storage.create_user.assert_has_calls(calls)
