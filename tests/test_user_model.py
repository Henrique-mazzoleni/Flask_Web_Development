import unittest
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        password = 'Cat'
        test_user = User(password=password)
        self.assertTrue(test_user.password_hash is not None)

    def test_no_password_getter(self):
        password = 'Cat'
        test_user = User(password=password)
        with self.assertRaises(AttributeError):
            test_user.password

    def test_password_verification(self):
        password = 'Cat'
        not_password = 'Dog'
        test_user = User(password=password)
        self.assertTrue(test_user.verify_password(password))
        self.assertFalse(test_user.verify_password(not_password))

    def test_salts_are_random(self):
        password = 'Cat'
        test_user = User(password=password)
        other_test_user = User(password=password)
        self.assertTrue(test_user.password_hash != other_test_user.password_hash)