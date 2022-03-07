"""Python module for testing 'chat_server' module."""

from unittest import mock, TestCase

from chat import chat_pb2
from chat.chat_storage import User, Message, EtcdStorage
from chat import chat_server


class TestChat(TestCase):
    """Tests Chat class."""

    @classmethod
    def setUpClass(cls):
        """Creates objects to be used by the tests."""
        cls.storage = mock.Mock()
        cls.chat = chat_server.Chat(cls.storage)
        cls.user1 = User(login="userA", full_name="AA AAA")
        cls.user2 = User(login="userB", full_name="BB BBB")
        

    def test_GetUsers(self):
        """Tests 'GetUsers' method."""
        self.storage.client.get_prefix.return_value = [self.user1, self.user2]
        self.storage.get_users_list.return_value = [self.user1, self.user2]
        users = [chat_pb2.User(login="userA", full_name="AA AAA"),
                 chat_pb2.User(login="userB", full_name="BB BBB")]
        expected = chat_pb2.GetUsersReply(users=users)
        result = self.chat.GetUsers(mock.Mock(), mock.Mock())
        self.assertEqual(expected, result)

    @mock.patch("chat.chat_storage.time.time")
    def test_SendMessage(self, mock_time):
        """Tests 'SendMessage' method."""
        mock_time.return_value = 1111
        self.storage.create_message = mock.Mock()
        request = mock.Mock(message=mock.Mock(login_from="userA",
                                              login_to = "userB",
                                              body = "Hello, you."))
        context = mock.Mock()
        expected = chat_pb2.SendMessageReply(
            status=f"Done! {request.message.login_to} received message " +
            f"from {request.message.login_from}!"
        )
        result = self.chat.SendMessage(request, context)
        self.storage.create_message.assert_called_with(
            Message(request.message.login_from, request.message.login_to, request.message.body))                                                  
        self.assertEqual(expected, result)

    @mock.patch("chat.chat_storage.time.sleep")
    def test_Subscribe(self, mock_time):
        """Tests 'Subscribe' method."""
        mock_time.return_value = None
        self.storage.get_user_messages = mock.Mock()
        self.storage.delete_user_message = mock.Mock()
        request = mock.Mock(login="B")
        context = mock.Mock()
        context.is_active.return_value = True
        self.storage.get_user_messages.return_value = [
            Message(login_from="A", login_to="B", body="Hello, you!", created_at=1234),
            Message(login_from="C", login_to="B", body="Hello!", created_at=12345)]
        messages = self.storage.get_user_messages(request.login)
        expected = (chat_pb2.Message(login_from=message.login_from,
                                     login_to=message.login_to,
                                     created_at=message.created_at,
                                     body=message.body) for message in messages)
        result = self.chat.Subscribe(request, context)
        result_list = [next(result), next(result), next(result)]
        calls = [mock.call(Message(login_from="A",login_to="B",
                                   body="Hello, you!", created_at=1234)), 
                 mock.call(Message(login_from='C', login_to='B',
                                   body='Hello!', created_at=12345))]
        self.storage.get_user_messages.assert_called_with("B")
        self.storage.delete_user_message.assert_has_calls(calls)
        self.assertListEqual(list(expected), result_list[:2])


class TestServerFunctions(TestCase):
    """Class for testing chat_server functions."""

    def test_create_users_list(self):
        """Tests 'create_users_list' method."""
        self.storage = mock.Mock()
        self.storage.create_user = mock.Mock()
        chat_server.create_users_list(self.storage)
        calls = [mock.call(User(login='user_A', full_name='AA AAA')),
                 mock.call(User(login='user_B', full_name='BB BBB')),
                 mock.call(User(login='user_C', full_name='CC CCC')),
                 mock.call(User(login='user_D', full_name='DD DDD'))]
        self.storage.create_user.assert_has_calls(calls)

    @mock.patch("chat.chat_server.os.environ")
    def test_initialize_storage(self, mock_os):
        """Tests 'cinitialize_storage' method."""
        mock_os.get.return_value = "etcd"
        storage = chat_server.initialize_storage('localhost', 2379)
        self.assertIsInstance(storage, EtcdStorage)