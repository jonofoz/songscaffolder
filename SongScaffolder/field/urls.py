from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.config, name="config"),
    path("<str:field_name>", views.config, name="config"),
    path("delete/<str:data_id>", views.delete, name="delete"),
]