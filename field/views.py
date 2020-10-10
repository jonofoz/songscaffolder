import json
import sys, os
sys.path.append(os.path.join("..", ".."))

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from field.models import UserData

UserModel = get_user_model()

@login_required
@csrf_exempt
def config(request, field_name):

    accepted_keys = ["chords", "feels", "genres", "influences", "instruments", "key-signatures", "moods", "themes", "time-signatures"]

    if field_name not in accepted_keys:
        return redirect("index")
    username = request.user.username
    user_data = UserData.objects.get(user=UserModel.objects.get(username=username))

    if request.method != "POST":
        field_data = user_data.scaffold_config.get(field_name, {})
        context = {
            "field_name": field_name,
            "field_data": field_data
        }
        return render(request, "pages/config.html", context)
    else:
        user_data.scaffold_config[field_name] = json.loads(request.POST["field_data"])
        user_data.save()
        return redirect("pages:index")

