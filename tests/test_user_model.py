import unittest
from flask import current_app
from app import create_app, db
from app.models import User, Permission, AnonymousUser, Role

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        password = 'Cat'
        email='test@test.com'
        test_user = User(email=email, password=password)
        self.assertTrue(test_user.password_hash is not None)

    def test_no_password_getter(self):
        password = 'Cat'
        email='test@test.com'
        test_user = User(email=email, password=password)
        with self.assertRaises(AttributeError):
            test_user.password

    def test_password_verification(self):
        password = 'Cat'
        not_password = 'Dog'
        email='test@test.com'
        test_user = User(email=email, password=password)
        self.assertTrue(test_user.verify_password(password))
        self.assertFalse(test_user.verify_password(not_password))

    def test_salts_are_random(self):
        password = 'Cat'
        email='test@test.com'
        email2='test2@test.com'
        test_user = User(email=email, password=password)
        other_test_user = User(email=email2, password=password)
        self.assertTrue(test_user.password_hash != other_test_user.password_hash)

    def test_user_role(self):
        email='john@example.com'
        password = 'cat'
        u = User(email=email, password=password)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_admin_role(self):
        email = current_app.config['FLASKY_ADMIN']
        password = 'secretpassword'
        u = User(email=email, password=password)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertTrue(u.can(Permission.ADMIN))
        
    def test_follow_following(self):
        test_user = {
            'email': 'test@test.com',
            'password': 'pass',
        }
        test_user2 = {
            'email': 'test2@test.com',
            'password': 'pass',
        }
        u = User(**test_user)
        u2 = User(**test_user2)
        self.assertFalse(u.is_following(u2))
        self.assertFalse(u2.is_followed_by(u))
        u.follow(u2)
        db.session.commit()
        self.assertTrue(u.is_following(u2))
        self.assertTrue(u2.is_followed_by(u))
        u.unfollow(u2)
        db.session.commit()
        self.assertFalse(u.is_following(u2))
        self.assertFalse(u2.is_followed_by(u))

