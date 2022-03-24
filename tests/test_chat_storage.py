"""Python module for testing chat_storage module."""

from unittest import TestCase, mock

from chat_storage import EtcdStorage, Message, User


class TestEtcdStorage(TestCase):
    """Tests EtcdStorage class."""

    @classmethod
    def setUpClass(cls):
        """Creates User and Message objects to be used by the tests."""
        cls.user1 = User(login="userA", full_name="AA AAA")
        cls.user2 = User(login="userB", full_name="BB BBB")
        cls.message1 = Message(
            login_from="user1", login_to="userB", body="Hello!", created_at=1234)
        cls.message2 = Message(
            login_from="user2", login_to="userB", body="Hello, you!", created_at=5678)

    @mock.patch("chat_storage.etcd3")
    def setUp(self, mock_etcd):
        """Creates client and storage objects to be used by the tests."""
        self.client = mock.Mock()
        mock_etcd.client.return_value = self.client
        self.storage = EtcdStorage(host="localhost", port=2379)

    def test_create_user(self):
        """Tests 'create_user' method."""
        self.client.put = mock.Mock()
        self.storage.create_user(self.user1)
        self.client.put.assert_called_once_with(
            "user.userA", '{"login": "userA", "full_name": "AA AAA"}')

    def test_create_message(self):
        """Tests 'create_message' method."""
        self.client.put = mock.Mock()
        self.storage.create_message(self.message1)
        self.client.put.assert_called_once_with(
            "message.userB.user1.1234",
            '{"login_from": "user1", "login_to": "userB", "body": "Hello!", "created_at": 1234}')

    def test_get_users_list(self):
        """Tests 'users_list' method."""
        self.client.get_prefix.return_value = [
            ('{"login": "userA", "full_name": "AA AAA"}'.encode(), "user1"),
            ('{"login": "userB", "full_name": "BB BBB"}'.encode(), "user2")]
        users = self.storage.get_users_list()
        expected = [self.user1, self.user2]
        self.client.get_prefix.assert_called_with("user.")
        self.assertListEqual(expected, users)

    def test_get_user_messages(self):
        """Tests 'get_user_messages' method."""
        self.client.get_prefix.return_value = [
            ('{"login_from": "user1","login_to": "userB",\
            "body": "Hello!","created_at": 1234}'.encode(), "message1"),
            ('{"login_from": "user2", "login_to": "userB",\
            "body": "Hello, you!", "created_at": 5678}'.encode(), "user2")]
        messages = self.storage.get_user_messages("userB")
        expected = [self.message1, self.message2]
        self.client.get_prefix.assert_called_with("message.userB.")
        self.assertListEqual(expected, messages)

    def test_delete_user_message(self):
        """Tests 'delete_user_message' method."""
        self.client.delete = mock.Mock()
        self.storage.delete_user_message(self.message1)
        self.client.delete.assert_called_once_with("message.userB.user1.1234")


class TestUserInstance(TestCase):
    """Tests User class."""

    def setUp(self):
        """Creates user data to be used by the tests."""
        self.user_data = {"login": 'user1', "full_name": "AA AAA"}

    def test_get_unique_key(self):
        """Tests get unique key method."""
        user = User(**self.user_data)
        key = user.get_unique_key()
        expected_key = "user.user1"
        self.assertEqual(expected_key, key)


class TestMessageInstance(TestCase):
    """Tests Message class."""

    def setUp(self):
        """Creates message data to be used by the tests."""
        self.message_data = {"login_from": "user1", "login_to": "user2",
                             "body": "Hello, you!", "created_at": 1234}

    def test_get_unique_key(self):
        """Tests get unique key method."""
        user = Message(**self.message_data)
        key = user.get_unique_key()
        expected_key = "message.user2.user1.1234"
        self.assertEqual(expected_key, key)
