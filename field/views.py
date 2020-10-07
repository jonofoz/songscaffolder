import json
import sys, os
sys.path.append(os.path.join("..", ".."))

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from field.models import UserData
from django.contrib.auth.models import User

chords = "chords"
feels = "feels"
genres = "genres"
influences = "influences"
instruments = "instruments"
key_signatures = "key-signatures"
moods = "moods"
themes = "themes"
time_signatures = "time-signatures"

# Create your views here.
@login_required
@csrf_exempt
def config(request, field_name):

    accepted_keys = [chords, feels, genres, influences, instruments, key_signatures, moods, themes, time_signatures]

    if field_name not in accepted_keys:
        return redirect("index")

    if request.method != "POST":
        field_data = request.session["metadata"]["user_data"]["scaffold_config"].get(field_name, {})
        context = {
            "field_name": field_name,
            "field_data": field_data
        }
        return render(request, "pages/config.html", context)
    else:
        new_field_data = json.loads(request.POST["field_data"])
        username = request.session["metadata"]["username"]
        user_data = UserData.objects.get(user=User.objects.get(username=username))
        user_data.scaffold_config[field_name] = new_field_data
        user_data.save()
        request.session["metadata"]["user_data"]["scaffold_config"][field_name] = new_field_data
        request.session.save()
        return redirect("pages:index")

