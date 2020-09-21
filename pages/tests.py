from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

ss_test_user_name = "SongScaffolderTestUser"
ss_test_user_pass = "4CKke4NXzWKsaKU"
# Create your tests here.

class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=ss_test_user_name, password=ss_test_user_pass)
        self.user.save()

        self.client = Client()

    def test_signup(self):
        pass


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


    def test_make_scaffold(self):
        # logged_in = self.client.login(username=ss_test_user_name, password=ss_test_user_pass)
        # logged_in = self.client.force_login()
        # response = client.post("/make-scaffold/", {"metadata":}, content_type="application/json").json()
        pass
