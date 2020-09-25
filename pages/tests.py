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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.driver = WebDriverFirefox()
        self.driver.implicitly_wait(10)
        self.actionchains = ActionChains(self.driver)


    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.clear_test_user_data()

    def login(self):
        driver = self.driver
        driver.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = driver.find_element_by_id("id_username")
        username_input.send_keys(self.username)
        password_input = driver.find_element_by_id("id_password")
        password_input.send_keys(ss_test_user_pass)
        driver.find_element_by_id("login_form").submit()
        WebDriverWait(driver, 5).until(
            EC.title_is("SongScaffolder")
        )

    def clear_test_user_data(self):
        db = connect_to_database(use_test_db=True)
        db["user_data"].delete_many({"username": {"$regex": "^SongScaffolderTestUser"}})

    def scroll_to(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def test_make_scaffold_no_data(self):
        driver = self.driver
        self.login()
        scaffold_button = driver.find_element_by_id("btn-make-scaffold")
        self.scroll_to(scaffold_button)
        self.actionchains.move_to_element(scaffold_button).click().perform()
        self.assertTrue(
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//td[text()='You selected nothing!']"))
            )
        )
        self.assertTrue(
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//td[text()='Please select a field to include.']"))
            )
        )

    def test_make_scaffold(self):
        driver = self.driver
        self.login()
        driver.switch_to_window(driver.window_handles[0])
        # CHORDS
        chord_specs = driver.find_element_by_id("define-specs-for_chords")
        self.scroll_to(chord_specs)
        self.actionchains.move_to_element(chord_specs).click().perform()
        btn_add_rows = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "button-add-rows"))
        )
        input_how_many = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "how-many-to-add"))
        )
        driver.switch_to_window(driver.window_handles[0])
        self.scroll_to(input_how_many)
        input_how_many.click()
        input_how_many.send_keys("5")
        btn_add_rows.click()

        new_rows = driver.find_elements_by_class_name("item-input.no-border")
        frequencies = driver.find_elements_by_class_name("pagination")
        keys_values = [
            ("5",  2),
            ("Maj7", 5),
            ("m9", 1),
            ("aug7", 3),
            ("Elektra", 4)
        ]
        for i, k_v in enumerate(keys_values):
            driver.implicitly_wait(1)
            key, value = k_v
            row = new_rows[i]
            row.send_keys(key)
            self.assertEqual(row.get_attribute("value"), key)
            frequency_tab = frequencies[i].find_elements_by_tag_name("li")[value - 1]
            frequency_tab.click()
            self.assertEqual(frequency_tab.text, str(value))

        driver.find_element_by_id("button-save").click()
        driver.find_element_by_class_name("display-4.logo").click()
        driver.find_element_by_id("define-specs-for_chords").click()

        new_rows = driver.find_elements_by_class_name("item-input.no-border")
        frequencies = driver.find_elements_by_class_name("pagination")
        self.assertEqual(len(new_rows), 5)
        self.assertEqual(len(frequencies), 5)
        for i, k_v in enumerate(keys_values):
            key, value = k_v
            self.assertEqual(new_rows[i].get_attribute("value"), key)
            self.assertEqual(frequencies[i].find_elements_by_tag_name("li")[value - 1].text, str(value))


    def test_cosmetic_things(self):
        driver = self.driver
        self.login()
        # Test hovering over help buttons
        for element_id, expected_text in [
            ("get-help-for-fields", "Checking these will include random selections of the corresponding field into the scaffold. These selections can be specified by clicking the appropriate button."),
            ("get-help-for-quantities", "These determine how many items from the corresponding field you want to include."),
            ("get-help-for-specifications", "Clicking these will allow you to specify the selections for the corresponding field.")
        ]:

            driver.switch_to_window(driver.window_handles[0])
            self.actionchains.move_to_element(driver.find_element_by_id(element_id)).perform()
            self.assertTrue(
                WebDriverWait(self.driver, 5).until(
                    EC.text_to_be_present_in_element((By.CLASS_NAME, "tooltip"), expected_text)
                )
            )
