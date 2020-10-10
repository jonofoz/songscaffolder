from django.db import models
from django.conf import settings
from django.contrib.auth import backends, get_user_model
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db.models import Q

UserModel = get_user_model()

class UserData(models.Model):

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    saved_scaffolds = ArrayField(
        JSONField(
            models.CharField(max_length=10, blank=True)
        ),
        size=10,
        default=list
    )
    scaffold_config = JSONField(default=dict)

    def __str__(self):
        return f"UserData | {self.user.username} | {self.user.email}"

class ModelBackend(backends.ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            pass