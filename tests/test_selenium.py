import re
import threading
import time
import unittest
from selenium import webdriver
from app import create_app, db, fake
from app.models import Role, User



class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls) -> None:
        # start Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        try:
            cls.client = webdriver.Chrome(chrome_options=options)
        except Exception:
            pass
    
        #skip these tests if the browser could not be started
        if cls.client:
            # create application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            #suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            # create the database and populate with some fake data
            db.create_all()
            Role.insert_roles()
            fake.users(10)
            fake.posts(10)

            # add an administrator user
            admin_role = Role.query.filter_by(name='Administrator').first()
            admin = User(email='gabi@Mazzuolo.com',
                         username='Gabi',
                         password='twix',
                         role=admin_role,
                         confirmed=True)
            db.session.add(admin)
            db.session.commit()

            # start the Flask server in a thread
            cls.server_thread = threading.Thread(
                target=cls.app.run,
                kwargs={'debug': False}
            )
            cls.server_thread.start()

            # give the server a second to ensure it is up
            time.sleep(1)
    
    @classmethod
    def tearDownClass(cls) -> None:
        if cls.client:
            #stop the Flask server and the browser
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.quit()
            cls.server_thread.join()

            #destroy database
            db.drop_all()
            db.session.remove()

            # remove application context
            cls.app_context.pop()

    def setUp(self) -> None:
        if not self.client:
            self.skipTest('Web browser not available.')
        
    def tearDown(self) -> None:
        pass

    def test_admin_home_page(self) -> None:
        # navigate to home page
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\s+Stranger!',
                                  self.client.page_source))