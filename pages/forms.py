from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UsernameField
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.utils.translation import gettext, gettext_lazy as _

UserModel = get_user_model()

class LoginForm(forms.Form):
    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'username'}),
        label=_("Email or Username")
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user


class UserSignupForm(UserCreationForm):

    class Meta:
        model = UserModel
        fields = ("email", "username")
        field_classes = {'email': forms.EmailField, "username": UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


