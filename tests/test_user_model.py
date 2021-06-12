import unittest
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        test_user = User(password = 'Cat')
        self.assertTrue(test_user.password_hash is not None)

    def test_no_password_getter(self):
        test_user = User(password = 'Cat')
        with self.assertRaises(AttributeError):
            test_user.password

    def test_password_verification(self):
        password = 'Cat'
        not_password = 'Dog'
        test_user = User(password=password)
        self.assertTrue(test_user.verify_password(password))
        self.assertFalse(test_user.verify_password(not_password))