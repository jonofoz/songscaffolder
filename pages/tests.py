import json
from lxml import html

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.utils import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from field.models import UserData

ss_test_user_name = "SongScaffolderTestUser"
ss_test_user_pass = "IsThi$Pa$$w0rdGoodEnough4Ye"

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


def clear_test_data():
    try:
        User.objects.get(username=ss_test_user_name).delete()
    except:
        pass

class BaseTestClass(TestCase):

    def setUp(self):
        self.username = ss_test_user_name
        self.client = Client()
        # Check if setup should be skipped.
        method = getattr(self, self._testMethodName)
        tags = getattr(method, 'tags', {})

        if 'skip_setup' in tags:
            return

        clear_test_data()

        self.user = User.objects.create_user(username=self.username, password=ss_test_user_pass)
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
        response = self.client.post(reverse("pages:signup"), {"username": self.username, "password1": ss_test_user_pass, "password2": ss_test_user_pass}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('/login/', 302)])
        self.assertEqual(response.context["user"].username, '')
        self.assertTrue("password" not in response.context)
        content_decoded = response.content.decode("utf-8")
        self.assertFalse(f"(Hi, {self.username}!)" in content_decoded)
        self.assertTrue("<title>\n        \nLogin\n\n    </title>" in content_decoded)
        # Test UserData
        user_data = UserData.objects.get(user=User.objects.get(username=self.username))
        self.assertEqual(user_data.saved_scaffolds, [])
        self.assertEqual(user_data.scaffold_config, {})

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

    def test_login_no_userdata(self):
        # Here we're going to prove that logging in as a valid user will generate a default UserData object
        # if the UserData object DNE for that user.
        self.user_data.delete()
        # GET
        response = self.client.get(reverse("pages:login"))
        self.assertEqual(response.resolver_match.func.__name__, "user_login")
        self.assertEqual(response.status_code, 200)
        # POST
        response = self.client.post(reverse("pages:login"), {"username": self.username, "password": ss_test_user_pass}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('/', 302)])
        # Now, let's check if the UserData is there.
        user_data = UserData.objects.get(user=self.user)
        self.assertEqual(user_data.user.username, ss_test_user_name)
        self.assertEqual(user_data.scaffold_config, {})
        self.assertEqual(user_data.saved_scaffolds, [])



    def test_config(self):
        response = self.client.post(reverse("pages:login"), {"username": self.username, "password": ss_test_user_pass}, follow=True)
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
        values = tree.xpath("//li[contains(@class, 'page-item') and contains(@class, 'active')]")
        self.assertEqual(len(keys), 5)
        self.assertEqual(len(values), 5)
        for i, k_v in enumerate(keys_values):
            k, v = k_v
            self.assertEqual(keys[i].value, k)
            self.assertEqual(int(values[i].text_content()), v)

    def test_make_scaffold_good(self):
        response = self.client.post(reverse("pages:login"), {"username": self.username, "password": ss_test_user_pass}, follow=True)

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


    def test_make_scaffold_missing_data(self):
        response = self.client.post(reverse("pages:login"), {"username": self.username, "password": ss_test_user_pass}, follow=True)

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