import os
import sys
import hashlib
import time
from random import randint
from datetime import datetime
sys.path.append("..")

from common.utils import connect_to_database

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.utils import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver as WebDriverFirefox

ss_test_user_name = "SongScaffolderTestUser"
ss_test_user_pass = "IsThi$Pa$$w0rdGoodEnough4Ye"
# Create your tests here.

def generate_test_username():
    name_hash = hashlib.md5()
    random_int_list = []
    for i in range(5):
        random_int_list.append(str(randint(0, 5000)))
    complicated_username_suffix = datetime.now().strftime("%H:%M:%S") + "_".join(random_int_list)
    name_hash.update(complicated_username_suffix.encode('ASCII'))
    return f"{ss_test_user_name}_{name_hash.hexdigest()}"


def clear_test_data():
    try:
        test_users = User.objects.filter(username__startswith="SongScaffolderTestUser")
        test_users.delete()
    except:
        pass
    db = connect_to_database(use_test_db=True)
    db["user_data"].delete_many({"username": {"$regex": "^SongScaffolderTestUser"}})

class BaseTestClass(TestCase):
    def setUp(self):
        self.username = generate_test_username()
        self.client = Client()
        # Check if setup should be skipped.
        method = getattr(self, self._testMethodName)
        tags = getattr(method,'tags', {})
        if 'skip_setup' in tags:
            return

        clear_test_data()

        self.user = User.objects.create_user(username=self.username, password=ss_test_user_pass)
        self.user.save()

    @classmethod
    def tearDownClass(cls):
        clear_test_data()
        super().tearDownClass()

class UserTestCase(BaseTestClass):

    @tag('skip_setup')
    def test_signup(self):
        # GET
        response = self.client.get(reverse("pages:signup"))
        self.assertEqual(response.resolver_match.func.__name__, "user_signup")
        self.assertEqual(response.status_code, 200)
        # POST
        response = self.client.post(reverse("pages:signup"), {"username": self.username, "password1": ss_test_user_pass, "password2": ss_test_user_pass}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('/login/', 302)])
        self.assertEqual(response.context["user"].username, '')
        self.assertTrue("password" not in response.context)
        content_decoded = response.content.decode("utf-8")
        self.assertFalse(f"(Hi, {self.username}!)" in content_decoded)
        self.assertTrue("<title>\n        \nLogin\n\n    </title>" in content_decoded)
        # TEST DB
        db = connect_to_database(use_test_db=True)
        user_cursor = db["user_data"].find({"username": self.username})
        self.assertEqual(user_cursor.count(), 1)
        self.assertEqual(user_cursor[0]["user_data"], {'saved_scaffolds': [], 'scaffold_config': {}})


    def test_login(self):
        # GET
        response = self.client.get(reverse("pages:login"))
        self.assertEqual(response.resolver_match.func.__name__, "user_login")
        self.assertEqual(response.status_code, 200)
        # POST
        response = self.client.post(reverse("pages:login"), {"username": self.username, "password": ss_test_user_pass}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('/', 302)])
        self.assertEqual(   response.context["user"].username, self.username)
        self.assertNotEqual(response.context["user"].password, ss_test_user_pass)
        content_decoded = response.content.decode("utf-8")
        self.assertTrue("<title>\n        \nSongScaffolder\n\n    </title>" in content_decoded)
        self.assertTrue(f"(Hi, {self.username}!)" in content_decoded)
        # TEST DB
        db = connect_to_database(use_test_db=True)
        user_cursor = db["user_data"].find({"username": self.username})
        self.assertEqual(user_cursor.count(), 1)
        self.assertEqual(user_cursor[0]["user_data"], {'saved_scaffolds': [], 'scaffold_config': {}})

    def test_make_scaffold(self):
        # logged_in = self.client.login(username=self.username, password=ss_test_user_pass)
        # logged_in = self.client.force_login()
        # response = client.post("/make-scaffold/", {"metadata":}, content_type="application/json").json()
        pass

class SeleniumTestsFirefox(BaseTestClass, StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriverFirefox()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        super(SeleniumTestsFirefox, self).setUp()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = self.selenium.find_element_by_id("id_username")
        username_input.send_keys(self.username)
        password_input = self.selenium.find_element_by_id("id_password")
        password_input.send_keys(ss_test_user_pass)
        self.selenium.find_element_by_id("login_form").submit()
        time.sleep(5)
        self.assertEqual(self.selenium.title, "SongScaffolder")