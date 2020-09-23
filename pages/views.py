import json
import sys, os
sys.path.append(os.path.join("..", ".."))
from common.utils import connect_to_database
from backend.scaffolder import SongScaffolder

from django import forms
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import LoginForm
from .tests import ss_test_user_name

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
        info = f"Checking this will include random <span class='tooltip-bold'>{title.lower()}</span> into the scaffold. These are defined under the corresponding <a class=\"fa fa-list fa-list-small\"></a> button."
        # info = f"Checking this will include random <span class='tooltip-bold'>{title.lower()}</span> into the scaffold. These are defined under <em>\"I Define Them Here.\"</em>"
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
                    db = connect_to_database(use_test_db=True if username.startswith(ss_test_user_name) else False)
                    user = db["auth_user"].find({"username": username})
                    # if user.count() > 0:
                    user = user[0]
                    user_data_cursor = db["user_data"].find({"id": user["id"]})

                    def remove_mongodb_id(d):
                        return {k: v for k, v in d.items() if k != "_id"}

                    if user_data_cursor.count() > 0:
                        user_data = remove_mongodb_id(user_data_cursor[0])
                    else:
                        user_data = {
                            "username": user["username"],
                            "user_data": {
                                "saved_scaffolds": [],
                                "scaffold_config": {}
                            }
                        }
                        db["user_data"].insert_one(user_data)
                    request.session["metadata"] = remove_mongodb_id(user_data)
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
            username = form.cleaned_data["username"]
            user_data = {
                "username": username,
                "user_data": {
                    "saved_scaffolds": [],
                    "scaffold_config": {}
                }
            }
            db = connect_to_database(use_test_db=True if username.startswith(ss_test_user_name) else False)
            db["user_data"].insert_one(user_data)
            return redirect("pages:login")
        else:
            raise forms.ValidationError("Form was invalid.")
    else:
        form = UserCreationForm()
    return render(request, "pages/auth/signup.html", {"form": form})

@login_required
def make_scaffold(request):
    attributes = {k: v["include"] for k,v in json.loads(request.GET["metadata"]).items()}
    quantities = {k: v["quantity"] for k, v in json.loads(request.GET["metadata"]).items() if "quantity" in v}
    with SongScaffolder(
        data=request.session["metadata"]["user_data"]["scaffold_config"],
        attributes=attributes,
        quantities=quantities,
        directives={}) as scaffolder:
        results = scaffolder.get_json_results()
        if results == {}:
            results = {"You selected nothing!": ["Please select a field to include."]}
        else:
            results = {k.replace("-", " ").title(): v for k, v in results.items()}
        return JsonResponse(results)

@login_required
def what_the_heck(request):
    return render(request, "pages/what-the-heck.html", )