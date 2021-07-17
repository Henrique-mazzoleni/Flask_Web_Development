import re
import unittest
from app import create_app, db
from app.models import User, Role

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self) -> None:
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Stranger' in response.data)

    def test_register_and_login(self):
        # register an account
        response = self.client.post('/auth/register', data={
            'email': 'gabriella@vuolo.com',
            'username': 'gabizinha',
            'password': 'buchecha',
            'password2': 'buchecha'
        })
        self.assertEqual(response.status_code, 302)

        # log in withh new account
        response = self.client.post('/auth/login', data={
            'email': 'gabriella@vuolo.com',
            'password': 'buchecha'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Hello' in response.get_data(as_text=True))
        self.assertTrue(re.search('Hello,\s+gabizinha!', response.get_data(as_text=True)))
        self.assertTrue('You have not confirmed your account yet!' in response.get_data(as_text=True))

        #send a confirmation token
        user = User.query.filter_by(email='gabriella@vuolo.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(f'/auth/accountconfirm/{token}', follow_redirects=True)
        user.check_token(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            'You have successfully confirmed your email' in response.get_data(as_text=True)
        )

        # logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('You have been logged out' in response.get_data(as_text=True))
