from django.urls import path, include

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.user_login, name="login"),
    path("signup/", views.user_signup, name="signup"),
    path("make-scaffold/", views.make_scaffold, name="make-scaffold"),
]