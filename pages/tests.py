import json
from lxml import html

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test.utils import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.sessions.models import Session
from field.models import UserData

UserModel = get_user_model()

ss_test_user_name  = "SongScaffolderTestUser"
ss_test_user_email = "SongScaffolderTestUser@geemayle.com"
ss_test_user_pass  = "IsThi$Pa$$w0rdGoodEnough4Ye"

example_saved_scaffolds = []
example_scaffold_config = {
    "chords": {
        "5": 3,
        "Maj7": 5,
        "m9": 4,
        "aug7": 0,
        "Elektra": 5
    },
    "genres": {
        "Hip-Hop": 4,
        "Ambient": 2,
        "Lo-Fi": 5
    },
    "instruments": {
        "Guitar": 4,
        "Piano": 3,
        "Kontakt": 5,
        "Serum": 5
    }
}
example_scaffold_directives = {
    'chords': {'include': True, 'quantity': 1},
    'feels': {'include': False},
    'genres': {'include': False},
    'influences': {'include': False},
    'instruments': {'include': False},
    'key-signatures': {'include': False},
    'moods': {'include': False},
    'themes': {'include': False},
    'time-signatures': {'include': False}
}

login_data_using_name  = {"username": ss_test_user_name,  "password": ss_test_user_pass}
login_data_using_email = {"username": ss_test_user_email, "password": ss_test_user_pass}

def clear_test_data():
    try:
        UserModel.objects.get(username=ss_test_user_name).delete()
    except:
        pass

class BaseTestClass(TestCase):

    def setUp(self):
        self.username = ss_test_user_name
        self.email = ss_test_user_email
        self.password = ss_test_user_pass
        self.client = Client()
        # Check if setup should be skipped.
        method = getattr(self, self._testMethodName)
        tags = getattr(method, 'tags', {})

        if 'skip_setup' in tags:
            return

        clear_test_data()

        self.user = UserModel.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.user.save()
        self.user_data = UserData(user=self.user, saved_scaffolds=example_saved_scaffolds, scaffold_config=example_scaffold_config)
        self.user_data.save()

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
        response = self.client.post(reverse("pages:signup"), {"username": self.username, "email": self.email, "password1": self.password, "password2": self.password}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('/login/', 302)])
        self.assertEqual(response.context["user"].username, '')
        self.assertTrue("password" not in response.context)
        content_decoded = response.content.decode("utf-8")
        self.assertFalse(f"(Hi, {self.username}!)" in content_decoded)
        self.assertTrue("<title>\n        \nLogin\n\n    </title>" in content_decoded)
        # Test UserData
        user_data = UserData.objects.get(user=UserModel.objects.get(username=self.username))
        self.assertEqual(user_data.saved_scaffolds, [])
        self.assertEqual(user_data.scaffold_config, {})

    def test_login(self):
        for login_data in [login_data_using_name, login_data_using_email]:
            # GET
            response = self.client.get(reverse("pages:login"))
            self.assertEqual(response.resolver_match.func.__name__, "user_login")
            self.assertEqual(response.status_code, 200)
            # POST
            response = self.client.post(reverse("pages:login"), login_data, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.redirect_chain, [('/', 302)])
            content_decoded = response.content.decode("utf-8")
            self.assertTrue("<title>\n        \nSongScaffolder\n\n    </title>" in content_decoded)
            self.assertTrue(f"(Hi, {self.username}!)" in content_decoded)
            Session.objects.all().delete()

    def test_login_invalid(self):
        response = self.client.post(reverse("pages:login"), {"username": self.username, "password": self.password+"Corn"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [])
        self.assertFalse(response.context["form"].is_valid())
        self.assertEqual(response.context["form"].errors["__all__"][0], "Sorry, that login was invalid. Please try again.")

    def test_login_no_userdata(self):
        # Here we're going to prove that logging in as a valid user will generate a default UserData object if
        # the UserData object DNE for that user. First, we have delete the UserData generated during setup.
        self.user_data.delete()
        # GET
        response = self.client.get(reverse("pages:login"))
        self.assertEqual(response.resolver_match.func.__name__, "user_login")
        self.assertEqual(response.status_code, 200)
        # POST
        response = self.client.post(reverse("pages:login"), login_data_using_email, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('/', 302)])
        # Now, let's check if the UserData is there.
        user_data = UserData.objects.get(user=self.user)
        self.assertEqual(user_data.user.username, self.username)
        self.assertEqual(user_data.scaffold_config, {})
        self.assertEqual(user_data.saved_scaffolds, [])

    def test_remove_user(self):
        # Here we're going to prove that removing a User will also remove their corresponding UserData.
        # First, we make sure both the user and the data exist.
        self.assertTrue(self.user)
        self.assertTrue(self.user_data)
        self.assertEqual(len(UserData.objects.all()), 1)
        self.user_data.delete()
        self.assertEqual(len(UserData.objects.all()), 0)

    def test_config(self):
        response = self.client.post(reverse("pages:login"), login_data_using_name, follow=True)
        # GET
        response = self.client.get("/config/chords")
        self.assertEqual(response.resolver_match.func.__name__, "config")
        self.assertEqual(response.status_code, 200)
        # POST
        response = self.client.post("/config/chords", {"field_data": json.dumps(self.user_data.scaffold_config["chords"])}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('/', 302)])
        content_decoded = response.content.decode("utf-8")
        # Here we make sure we go back to the homepage.
        self.assertTrue("<title>\n        \nSongScaffolder\n\n    </title>" in content_decoded)
        # GET (Checking if results were actually saved)
        response = self.client.get("/config/chords")
        tree = html.fromstring(response.content)
        keys_values = [(k,v) for k,v in self.user_data.scaffold_config["chords"].items()]
        keys = tree.xpath("//input[@placeholder='Edit Me!']")
        keys = sorted([k.value for k in keys])
        values = tree.xpath("//li[contains(@class, 'page-item') and contains(@class, 'active')]")
        values = sorted([v.text_content() for v in values])
        self.assertEqual(len(keys), 5)
        self.assertEqual(len(values), 5)
        # Here we assert that the HTML content reflects the user's data.
        self.assertEqual(keys,   sorted([i[0]      for i in keys_values]))
        self.assertEqual(values, sorted([str(i[1]) for i in keys_values]))

    def test_make_scaffold_good(self):
        response = self.client.post(reverse("pages:login"), login_data_using_email, follow=True)

        # Test making scaffold with 1 chord requested
        directives = example_scaffold_directives.copy()
        response = self.client.post(reverse("pages:make-scaffold"), {"directives": json.dumps(directives)}, follow=True)
        content_decoded = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content_decoded["chords"]), 1)

        # Test making scaffold with 3 chords requested
        directives["chords"]["quantity"] = 3
        response = self.client.post(reverse("pages:make-scaffold"), {"directives": json.dumps(directives)}, follow=True)
        content_decoded = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content_decoded["chords"]), 3)

        # Test making scaffold with more chords than are available
        directives["chords"]["quantity"] = 10
        response = self.client.post(reverse("pages:make-scaffold"), {"directives": json.dumps(directives)}, follow=True)
        content_decoded = json.loads(response.content.decode("utf-8"))
        # It should be 4, since the 'aug7' chord has a frequency of 0
        self.assertEqual(len(content_decoded["chords"]), 4)
        self.assertEqual(sorted(content_decoded["chords"]), ['5', 'Elektra', 'Maj7', 'm9'])

        # Let's change 'aug7's frequency in the user's data
        self.user_data.scaffold_config["chords"]["aug7"] = 1
        self.user_data.save()
        response = self.client.post(reverse("pages:make-scaffold"), {"directives": json.dumps(directives)}, follow=True)
        content_decoded = json.loads(response.content.decode("utf-8"))
        # It should be 5 now
        self.assertEqual(len(content_decoded["chords"]), 5)
        self.assertEqual(sorted(content_decoded["chords"]), ['5', 'Elektra', 'Maj7', 'aug7', 'm9'])

        # Here we're making sure a test doesn't return the same results more
        # than 3 times in a row given a sufficiently large dataset.
        directives["chords"]["quantity"] = 3
        last_results = None
        results_are_different = False
        for i in range(4):
            response = self.client.post(reverse("pages:make-scaffold"), {"directives": json.dumps(directives)}, follow=True)
            new_results = json.loads(response.content.decode("utf-8"))["chords"]
            if last_results == None:
                last_results = new_results
            else:
                if last_results != new_results:
                    results_are_different = True
                    break
                else:
                    last_results = new_results
        self.assertTrue(results_are_different)


    def test_make_scaffold_missing_data(self):
        response = self.client.post(reverse("pages:login"), login_data_using_name, follow=True)

        # Test making scaffold with no feels, even though they're requested
        directives = example_scaffold_directives.copy()
        directives["chords"]["quantity"] = 3
        directives["feels"]["quantity"]  = 3
        directives["feels"]["include"]   = True
        response = self.client.post(reverse("pages:make-scaffold"), {"directives": json.dumps(directives)}, follow=True)
        content_decoded = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content_decoded["chords"]), 3)
        self.assertEqual(len(content_decoded["feels"]), 1)
        self.assertEqual(content_decoded["feels"][0], "UNDEFINED: you have no data for this!")