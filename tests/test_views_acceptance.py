import os
import unittest
import multiprocessing
import time
from urlparse import urlparse

from werkzeug.security import generate_password_hash
from splinter import Browser

# Configure our app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog import models
from blog.database import Base, engine, session

'''
Tests to Perform:
	Make sure all the routes don't return "404"
X	Adding a Post
X	Deleting a Post
X	Editing/Updating a Post
	Logout Function working
'''

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.browser = Browser("phantomjs")

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = models.User(name="Alice", email="alice@example.com",
                                password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()
        port = int(os.environ.get('PORT', 8080))
        self.process = multiprocessing.Process(target=app.run, kwargs = {'host':'0.0.0.0','port':8080})
        self.process.start()
        time.sleep(1)

    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        self.process.terminate()
        Base.metadata.drop_all(engine)
        self.browser.quit()
    
    def login(self):
        """ Log into the site """
        self.browser.visit("http://0.0.0.0:8080/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.status_code.is_success(),True)
        self.assertEqual(self.browser.url, "http://0.0.0.0:8080/")
        
    def testAddPost(self):
        self.login()
        print 'We are logged in:'
        self.browser.visit("http://0.0.0.0:8080/post/add")
        self.browser.fill("title", "This is an example post")
        self.browser.fill("content", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.status_code.is_success(),True)
        self.assertEqual(self.browser.url, "http://0.0.0.0:8080/")
        self.assertEqual(self.browser.is_text_present('This is an example post'),True)

    def testDeletePost(self):
      self.login()
      self.testAddPost()
      self.browser.visit("http://0.0.0.0:8080/post/1/delete")
      self.browser.visit("http://0.0.0.0:8080/")      
      self.assertEqual(self.browser.is_text_present('This is an example post'),False)

    def testUpdatePost(self):
      self.login()
      self.testAddPost()
      self.browser.visit("http://0.0.0.0:8080/post/1/edit")
      self.browser.fill("title", "This is an example post UPDATED TITLE")
      self.browser.fill("content", "test NEW CONTENT")
      button = self.browser.find_by_css("button[type=submit]")
      button.click()
      self.assertEqual(self.browser.status_code.is_success(),True)
      self.assertEqual(self.browser.url, "http://0.0.0.0:8080/")
      self.assertEqual(self.browser.is_text_present('UPDATED TITLE'),True)
      self.assertEqual(self.browser.is_text_present('NEW CONTENT'),True)
        
    def testLoginCorrect(self):
        self.browser.visit("http://0.0.0.0:8080/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.status_code.is_success(),True)
        self.assertEqual(self.browser.url, "http://0.0.0.0:8080/")

    def testLogout(self):
      self.testLoginCorrect()
      self.browser.visit("http://0.0.0.0:8080/logout")
      self.assertEqual(self.browser.status_code.is_success(),True)
      self.assertEqual(self.browser.url, "http://0.0.0.0:8080/")
      self.assertTrue(self.browser.find_link_by_href('/login'))
      
    def testLoginIncorrect(self):
        self.browser.visit("http://0.0.0.0:8080/login")
        self.browser.fill("email", "bob@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.status_code.is_success(),True)
        self.assertEqual(self.browser.url, "http://0.0.0.0:8080/login")

if __name__ == "__main__":
    unittest.main()