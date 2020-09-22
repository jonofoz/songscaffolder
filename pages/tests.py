import os, sys
sys.path.append("..")

from common.utils import connect_to_database

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.utils import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver


ss_test_user_name = "SongScaffolderTestUser"
ss_test_user_pass = "IsThi$Pa$$w0rdGoodEnough4Ye"
# Create your tests here.

class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=ss_test_user_name, password=ss_test_user_pass)
        self.user.save()

        self.client = Client()

    @tag('skip_setup')
    def test_signup(self):
        # GET
        response = self.client.get(reverse("pages:signup"))
        self.assertEqual(response.resolver_match.func.__name__, "user_signup")
        self.assertEqual(response.status_code, 200)
        # POST
        response = self.client.post(reverse("pages:signup"), {"username": ss_test_user_name, "password1": ss_test_user_pass, "password2": ss_test_user_pass, "use_test_db":True}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertEqual(response.context["user"].username, '')
        self.assertTrue("password" not in response.context)
        content_decoded = response.content.decode("utf-8")
        self.assertFalse(f"(Hi, {ss_test_user_name}!)" in content_decoded)
        self.assertTrue("<title>\n        \nSign Up\n\n    </title>" in content_decoded)
        # TEST DB
        db = connect_to_database(use_test_db=True)
        user_cursor = db["user_data"].find({"username": ss_test_user_name})
        self.assertEqual(user_cursor.count(), 1)
        self.assertEqual(user_cursor[0]["user_data"], {'saved_scaffolds': [], 'scaffold_config': {}})


    def test_login(self):
        # GET
        response = self.client.get(reverse("pages:login"))
        self.assertEqual(response.resolver_match.func.__name__, "user_login")
        self.assertEqual(response.status_code, 200)
        # POST
        response = self.client.post(reverse("pages:login"), {"username": ss_test_user_name, "password": ss_test_user_pass, "use_test_db":True}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('/', 302)])
        self.assertEqual(   response.context["user"].username, ss_test_user_name)
        self.assertNotEqual(response.context["user"].password, ss_test_user_pass)
        content_decoded = response.content.decode("utf-8")
        self.assertTrue("<title>\n        \nSongScaffolder\n\n    </title>" in content_decoded)
        self.assertTrue(f"(Hi, {ss_test_user_name}!)" in content_decoded)
        # TEST DB
        db = connect_to_database(use_test_db=True)
        user_cursor = db["user_data"].find({"username": ss_test_user_name})
        self.assertEqual(user_cursor.count(), 1)
        self.assertEqual(user_cursor[0]["user_data"], {'saved_scaffolds': [], 'scaffold_config': {}})

    def test_make_scaffold(self):
        # logged_in = self.client.login(username=ss_test_user_name, password=ss_test_user_pass)
        # logged_in = self.client.force_login()
        # response = client.post("/make-scaffold/", {"metadata":}, content_type="application/json").json()
        pass

class SeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        # import pdb;pdb.set_trace()
        # self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
        # username_input = self.selenium.find_element_by_name("username")
        # username_input.send_keys('myuser')
        # password_input = self.selenium.find_element_by_name("password")
        # password_input.send_keys('secret')
        # self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
        pass