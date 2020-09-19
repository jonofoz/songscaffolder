import json
import sys, os
sys.path.append(os.path.join("..", ".."))
from common.utils import connect_to_database

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from . import models

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
        return render(request, "pages/config.html", context=context)
    else:
        db = connect_to_database()
        user_id = request.session["metadata"]["id"]
        if db["user_data"].find({"id": user_id}).count() == 0:
            raise Exception(f"An unexpected error occurred: the user_data dict for user id {user_id} not found in database!")
        if field_name not in request.session["metadata"]["user_data"]["scaffold_config"]:
            request.session["metadata"]["user_data"]["scaffold_config"][field_name] = {}
        db["user_data"].update_one({"id": user_id}, {"$set": {f'user_data.scaffold_config.{field_name}': request.session["metadata"]["user_data"]["scaffold_config"][field_name]}})
        print("Changes saved")
        return redirect('pages:index')
    return redirect('pages:index')

@login_required
@csrf_exempt
def save_changes(request, field_name):
    new_field_data = json.loads(request.POST["field_data"])
    db = connect_to_database()
    user_id = request.session["metadata"]["id"]
    db["user_data"].update_one({"id": user_id}, {"$set": {f'user_data.scaffold_config.{field_name}': new_field_data}})
    request.session["metadata"]["user_data"]["scaffold_config"][field_name] = new_field_data
    request.session.save()
    return redirect('pages:index')


@login_required
def delete(request, data_id):
    print(data_id)
    data_id_split = data_id.replace("-over-", "/").replace("-space-", " ").split("-")
    try:
        if len(data_id_split) == 2:
            del request.session["metadata"]["user_data"]["scaffold_config"][data_id_split[0]][data_id_split[1]]
        elif len(data_id_split) == 3:
            del request.session["metadata"]["user_data"]["scaffold_config"][data_id_split[0]][data_id_split[1]][data_id_split[2]]
        elif len(data_id_split) == 4:
            del request.session["metadata"]["user_data"]["scaffold_config"][data_id_split[0]][data_id_split[1]][data_id_split[2]][data_id_split[3]]
        request.session.save()
    except:
        pass
    finally:
        return redirect('field:config', data_id_split[0])