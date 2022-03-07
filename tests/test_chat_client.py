"""Python module for testing 'chat_client' module."""

from unittest import mock, TestCase

from chat import chat_pb2
from chat import chat_client


class TestChatClient(TestCase):
    """Class for testing chat_client functions."""

    def test_message_data_valid_or_raiserror(self):
        """Tests 'message_data_valid_or_raiserror' method and check raiserror."""
        args = mock.Mock(message=False)
        with self.assertRaises(chat_client.IncorrectDataError) as err:
            chat_client.message_data_valid_or_raiserror(args)
        expected = "Incorrect data. Please, check action or data."
        self.assertEqual(str(err.exception), expected)

    def test_subscribe_data_valid_or_raiserror(self):
        """Tests 'subscribe_data_valid_or_raiserror' method and check raiserror."""
        args = mock.Mock(subscribe=False)
        with self.assertRaises(chat_client.IncorrectDataError) as err:
            chat_client.subscribe_data_valid_or_raiserror(args)
        expected = "Incorrect data. Please, check action or data."
        self.assertEqual(str(err.exception), expected)
    
    @mock.patch("chat.chat_client.get_users_list")
    def test_valid_choose_action_users(self, mock_get_users_list):
        """Tests 'choose_action' method with valid data."""
        stub = mock.Mock()
        chat_client.choose_action(mock.Mock(action="users"), stub)
        mock_get_users_list.assert_called_once_with(stub)

    @mock.patch("chat.chat_client.send_message")
    def test_unvalid_choose_action_users(self, mock_send_message):
        """Tests 'choose_action' method with unvalid data."""
        chat_client.choose_action(mock.Mock(action="users"), mock.Mock())
        mock_send_message.assert_not_called()

    @mock.patch("chat.chat_client.send_message")
    def test_valid_choose_action_message(self, mock_send_message):
        """Tests 'choose_action' method with valid data."""
        stub = mock.Mock()
        args = mock.Mock(action="message")
        chat_client.choose_action(args, stub)
        mock_send_message.assert_called_once_with(args, stub)

    @mock.patch("chat.chat_client.subscribe")
    def test_valid_choose_action_subscribe(self, mock_subscribe):
        """Tests 'choose_action' method with valid data."""
        args = mock.Mock(action="subscribe")
        stub = mock.Mock()
        chat_client.choose_action(args, stub)
        mock_subscribe.assert_called_once_with(args, stub)
    
    def test_get_users_list(self):
        """Tests 'get_users_list' method."""
        stub = mock.Mock(GetUsers=mock.Mock())
        chat_client.get_users_list(stub)
        stub.GetUsers.assert_called_once_with(chat_pb2.GetUsersRequest())

    def test_send_message(self):
        """Tests 'send_message' method."""
        args = mock.Mock(message=["userA", "userB", "Hello."])
        stub = mock.Mock()
        stub.SendMessage = mock.Mock()
        chat_client.send_message(args, stub) 
        message = chat_pb2.Message(login_from="userA",
                               login_to="userB",
                               body="Hello.")
        stub.SendMessage.assert_called_once_with(chat_pb2.SendMessageRequest(message=message))

    def test_subscribe(self):
        """Tests 'subscribe' method."""
        args = mock.Mock(subscribe="userA")
        stub = mock.Mock()
        stub.Subscribe = mock.Mock()
        stub.Subscribe.return_value = ["message1", "message2", "message3"]
        chat_client.subscribe(args, stub)
        stub.Subscribe.assert_called_once_with(chat_pb2.SubscribeRequest(login=args.subscribe))
