import json
import sys, os

sys.path.append(os.path.join("..", ".."))
from backend.scaffolder import SongScaffolder

from django import forms
from field.models import UserData
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import backends, get_user_model
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import LoginForm, UserSignupForm

UserModel = get_user_model()

# Create your views here.
@login_required
def index(request):
    context = {
        "fields": []
    }

    for title in ["Chords" "Feels", "Genres", "Influences", "Instruments", "Key Signatures", "Moods", "Themes", "Time Signatures"]:
        info = f"Checking this will include random results from the below fields into the scaffold. The data for these results are defined under the corresponding <a class=\"fa fa-list fa-list-small\"></a> button."
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
            user_data = UserData.objects.get_or_create(user=UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username)))[0]
            return HttpResponseRedirect(reverse('pages:index'))
    else:
        form = LoginForm()

    return render(request, "pages/auth/login.html", {"form": form})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("pages:login"))

def user_signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            username = form.cleaned_data["username"]
            user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
            user_data = UserData(user=user, saved_scaffolds=[], scaffold_config={})
            user_data.save()
            return redirect("pages:login")
    else:
        form = UserSignupForm()
    return render(request, "pages/auth/signup.html", {"form": form})

@login_required
@csrf_exempt
def make_scaffold(request):
    directives = json.loads(request.POST["directives"])
    attributes = {k: v["include"]  for k, v in directives.items()}
    quantities = {k: v["quantity"] for k, v in directives.items() if "quantity" in v}
    user_data = UserData.objects.get(user=UserModel.objects.get(Q(username__iexact=request.user.username) | Q(email__iexact=request.user.email)))
    metadata = user_data.scaffold_config
    with SongScaffolder(
        metadata=metadata,
        attributes=attributes,
        quantities=quantities) as scaffolder:
        results = scaffolder.get_json_results()
        if results == {}:
            results = {"You selected nothing!": ["Please select a field to include."]}
        else:
            if "use_title_case" in request.POST and request.POST["use_title_case"] == 'true':
                results = {k.replace("-", " ").title(): v for k, v in results.items()}
            else:
                results = {k.replace("-", " "): v for k, v in results.items()}
        return JsonResponse(results)

@login_required
def what_the_heck(request):
    return render(request, "pages/what-the-heck.html", )