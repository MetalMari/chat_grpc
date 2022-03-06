"""Python module for testing 'chat_client' module."""

from unittest import mock, TestCase

from chat import chat_pb2
from chat import chat_client


class TestChatClient(TestCase):
    """Class for testing chat_client functions."""

    def test_message_data_valid_or_raiserror(self):
        """Tests 'message_data_valid_or_raiserror' method and check raiserror."""
        args = mock.Mock(message = False)
        self.assertRaises(chat_client.IncorrectDataError,
                          lambda: chat_client.message_data_valid_or_raiserror(args))

    def test_subscribe_data_valid_or_raiserror(self):
        """Tests 'subscribe_data_valid_or_raiserror' method and check raiserror."""
        args = mock.Mock(subscribe = False)
        self.assertRaises(chat_client.IncorrectDataError,
                          lambda: chat_client.subscribe_data_valid_or_raiserror(args))
    
    @mock.patch("chat.chat_client.get_users_list")
    def test_valid_choose_action_users(self, mock_get_users_list):
        """Tests 'choose_action' method with valid data."""
        chat_client.choose_action(mock.Mock(action = "users"), mock.Mock())
        self.assertTrue(mock_get_users_list.called)

    @mock.patch("chat.chat_client.send_message")
    def test_unvalid_choose_action_users(self, mock_send_message):
        """Tests 'choose_action' method with unvalid data."""
        chat_client.choose_action(mock.Mock(action = "users"), mock.Mock())
        self.assertFalse(mock_send_message.called)

    @mock.patch("chat.chat_client.send_message")
    def test_valid_choose_action_message(self, mock_send_message):
        """Tests 'choose_action' method with valid data."""
        chat_client.choose_action(mock.Mock(action = "message"), mock.Mock())
        self.assertTrue(mock_send_message.called)

    @mock.patch("chat.chat_client.subscribe")
    def test_valid_choose_action_subscribe(self, mock_subscribe):
        """Tests 'choose_action' method with valid data."""
        chat_client.choose_action(mock.Mock(action = "subscribe"), mock.Mock())
        self.assertTrue(mock_subscribe.called)
    
    def test_get_users_list(self):
        """Tests 'get_users_list' method."""
        chat_pb2.GetUsersRequest = mock.Mock()
        stub = mock.Mock()
        stub.GetUsers = mock.Mock()
        chat_client.get_users_list(stub)
        stub.GetUsers.assert_called()

    def test_send_message(self):
        """Tests 'send_message' method."""
        chat_pb2.SendMessageRequest = mock.Mock()
        args = mock.Mock()
        stub = mock.Mock()
        with mock.patch.object(args, 'message', ["userA", "userB", "Hello."]):
            stub.SendMessage = mock.Mock()
            chat_pb2.Message = mock.Mock()
            chat_client.send_message(args, stub)  
            stub.SendMessage.assert_called()

    def test_subscribe(self):
        """Tests 'subscribe' method."""
        args = mock.Mock(subscribe="userA")
        chat_pb2.SubscribeRequest = mock.Mock()
        stub = mock.Mock()
        stub.Subscribe = mock.Mock()
        stub.Subscribe.return_value = ["message1", "message2", "message3"]
        chat_client.subscribe(args, stub)
        stub.Subscribe.assert_called()
