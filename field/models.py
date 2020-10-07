from djongo import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField, JSONField

# Create your models here.

class UserData(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    saved_scaffolds = ArrayField(
        JSONField(
            models.CharField(max_length=10, blank=True)
        ),
        size=10,
        default=list
    )
    scaffold_config = JSONField(default=dict)

    def __str__(self):
        return f"UserData | {self.user.username}"