import sys, os
sys.path.append(os.path.join("..", ".."))
from common.utils import connect_to_database

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import LoginForm

# Create your views here.
@login_required
def index(request):
    context = {
        "fields": []
    }

    for title, *_, info in [
        ("Chords", "Checking this will include random chords into the scaffold. These chords are specified by clicking the respective list icon."),
        ("Feels", ""),
        ("Genres", ""),
        ("Influences", ""),
        ("Instruments", ""),
        ("Key Signatures", ""),
        ("Moods", ""),
        ("Themes", ""),
        ("Time Signatures", ""),
    ]:
        info = f"Checking this will include random <span class='tooltip-bold'>{title.lower()}</span> into the scaffold. These are specified under <em>\"Here's My Specs.\"</em>"
        context["fields"].append ({
            "title": title,
            "id": title.replace(" ","-").lower(),
            "info": info
        })
    return render(request, 'pages/index.html', context=context)

def user_login(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            authorized_user = authenticate(username=username, password=password)
            if authorized_user:
                if authorized_user.is_active:
                    login(request, authorized_user)
                    db = connect_to_database()
                    user = db["auth_user"].find({"username": username})[0]

                    user_data_cursor = db["user_data"].find({"id": user["id"]})
                    if user_data_cursor.count() > 0:
                        user_data = {k:v for k,v in user_data_cursor[0].items() if k != "_id"}
                    else:
                        user_data = {
                            "id": user["id"],
                            "username": user["username"],
                            "user_data": {
                                "saved_scaffolds": [],
                                "scaffold_config": {}
                            }
                        }
                        db["user_data"].insert_one(user_data)
                    request.session["metadata"] = user_data
                    request.session.save()
                    return HttpResponseRedirect(reverse('pages:index'))
                else:
                    pass

    else:
        form = LoginForm()

    return render(request, "pages/auth/login.html", {"form": form})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("pages:login"))

def user_signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect("pages:index")
        else:
            # raise forms.ValidationError("Form was invalid.")
            print("Form was invalid.")
    else:
        form = UserCreationForm()
    return render(request, "pages/auth/signup.html", {"form": form})

@login_required
def make_scaffold(request):
    pass