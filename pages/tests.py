import os
import sys
import hashlib
import time
import json
import requests
from random import randint
from datetime import datetime

sys.path.append("..")
from common.utils import connect_to_database

from selenium.webdriver.firefox.webdriver import WebDriver as WebDriverFirefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.utils import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


ss_test_user_name = "SongScaffolderTestUser"
ss_test_user_pass = "IsThi$Pa$$w0rdGoodEnough4Ye"
example_saved_scaffolds = []
example_scaffold_config = {
    "chords": {
        "5": 3,
        "Maj7": 5,
        "m9": 4,
        "aug7": 3,
        "Elektra": 5
    },
    "Genres": {
        "Hip-Hop": 4,
        "Ambient": 2,
        "Lo-Fi": 5
    },
    "Instruments": {
        "Guitar": 4,
        "Piano": 3,
        "Kontakt": 5,
        "Serum": 5
    }
}
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

    def tearDown(self):
        clear_test_data()


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
        cls.actionchains = ActionChains(cls.selenium)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.clear_test_user_data()

    def login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = self.selenium.find_element_by_id("id_username")
        username_input.send_keys(self.username)
        password_input = self.selenium.find_element_by_id("id_password")
        password_input.send_keys(ss_test_user_pass)
        self.selenium.find_element_by_id("login_form").submit()
        WebDriverWait(self.selenium, 5).until(
            EC.title_is("SongScaffolder")
        )

    def update_test_user_data(self):
        db = connect_to_database(use_test_db=True)
        db["user_data"].update_one({"username": self.username}, {"$set": {f'user_data.scaffold_config': example_scaffold_config}})

    def clear_test_user_data(self):
        db = connect_to_database(use_test_db=True)
        db["user_data"].delete_many({"username": {"$regex": "^SongScaffolderTestUser"}})

    def scroll_to(self, element):
        self.selenium.execute_script("arguments[0].scrollIntoView();", element)

    def test_login(self):
        self.login()
        self.assertTrue(
            WebDriverWait(self.selenium, 5).until(
                EC.title_is("SongScaffolder")
            )
        )


    def test_cosmetic_things(self):
        self.login()

        # Test hovering over help buttons
        for element_id, expected_text in [
            ("get-help-for-fields", "Checking these will include random selections of the corresponding field into the scaffold. These selections can be specified by clicking the appropriate button."),
            ("get-help-for-quantities", "These determine how many items from the corresponding field you want to include."),
            ("get-help-for-specifications", "Clicking these will allow you to specify the selections for the corresponding field.")
        ]:
            help_bubble = self.selenium.find_element_by_id(element_id)
            self.actionchains.move_to_element(help_bubble).perform()
            self.assertTrue(
            WebDriverWait(self.selenium, 5).until(
                    EC.text_to_be_present_in_element((By.CLASS_NAME, "tooltip"), expected_text)
                )
            )
