from django import forms
from django.core import validators
from django.contrib.auth.models import User
from django.contrib.auth.forms import UsernameField
from django.utils.translation import gettext, gettext_lazy as _

class LoginForm(forms.Form):
    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'username'})
    )
    email = forms.EmailField(label=_("Email"), required=False)
    # verify_email = forms.EmailField(label=_("Re-type Email"))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        # if cleaned_data["email"] != cleaned_data["verify_email"]:
        #     raise forms.ValidationError("Emails did not match.")
