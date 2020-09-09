from djongo import models

# Create your models here.

class Field(models.Model):

    field_name = models.CharField(max_length=25, unique=True)
    field_quantity = models.PositiveIntegerField()
    field_randomize = models.PositiveIntegerField()

    def __str__(self):
        return str(self.field_name)