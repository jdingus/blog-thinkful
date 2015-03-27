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

from selenium import webdriver

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
        self.process = multiprocessing.Process(target=app.run(host='localhost',port=8080))
        self.process.start()
        time.sleep(1)


    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        self.process.terminate()
        Base.metadata.drop_all(engine)
        self.browser.quit()

    def testLoginCorrect(self):
			
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)
        self.driver.get("https://duckduckgo.com/")
        self.driver.find_element_by_id('search_form_input_homepage').send_keys("realpython")
        self.driver.find_element_by_id("search_button_homepage").click()
        print self.driver.current_url
        self.driver.quit()
			
#         self.browser.visit("http://0.0.0.0:8080/login")
#         self.browser.fill("email", "alice@example.com")
#         self.browser.fill("password", "test")
#         button = self.browser.find_by_css("button[type=submit]")
#         button.click()
#         self.assertEqual(self.browser.url, "http://0.0.0.0:8080/")

    def testLoginIncorrect(self):
        self.browser.visit("http://0.0.0.0:8080/login")
        self.browser.fill("email", "bob@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://0.0.0.0:8080/login")

if __name__ == "__main__":
    unittest.main()