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
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import LoginForm
from .tests import ss_test_user_name
from field.models import UserData

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
    if request.user.is_authenticated:
        return redirect(reverse('pages:index'))
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            authorized_user = form.login(request)
            login(request, authorized_user)
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user_data = UserData.objects.get(user=User.objects.get(username=username))
            metadata = {
                "username": user_data.user.username,
                "user_data": {
                    "saved_scaffolds": user_data.saved_scaffolds,
                    "scaffold_config": user_data.scaffold_config
                }
            }
            request.session["metadata"] = metadata
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
            user = User.objects.get(username=username)
            user_data = UserData(user=user, saved_scaffolds=[], scaffold_config={})
            user_data.save()
            return redirect("pages:login")
        else:
            raise forms.ValidationError(form.errors)
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