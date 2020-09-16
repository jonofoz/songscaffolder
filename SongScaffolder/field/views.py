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

def get_dict_depth(d):
    return max(get_dict_depth(v) if isinstance(v,dict) else 0 for v in d.values()) + 1

# Create your views here.
@login_required
def config(request, field_name):

    accepted_keys = [chords, feels, genres, influences, instruments, key_signatures, moods, themes, time_signatures]

    if field_name not in accepted_keys:
        return redirect("index")

    if request.method != "POST":
        # TODO: Remove sample data once user_data is populated on login.
        if "user_data" in request.session["metadata"]:
            request.session["metadata"]["user_data"] = {
                "chords": {
                    "5": 5,
                    "M7": 5,
                    "6": 5,
                    "6/9": 5,
                    "6add9": 5,
                    "11": 5,
                    "11b9": 5,
                    "13": 5,
                    "13#9": 5,
                    "13b5b9": 5,
                    "13b9": 5,
                    "6sus4": 5,
                    "7": 5,
                    "7#11": 5,
                    "7#5": 5,
                    "7#5#9": 5,
                    "7#5b9": 5,
                    "7#9": 5,
                    "7add11": 5,
                    "7add13": 5,
                    "7b5": 5,
                    "7b5b9": 5,
                    "7b9": 5,
                    "7sus2": 5,
                    "7sus4": 5,
                    "9": 5,
                    "9#11": 5,
                    "9#5": 5,
                    "9b13": 5,
                    "9b5": 5,
                    "9sus2": 5,
                    "9sus4": 5,
                    "add9": 5,
                    "aug": 5,
                    "augsus2": 5,
                    "augsus4": 5,
                    "m11": 5,
                    "m13": 5,
                    "m6": 5,
                    "m6add9": 5,
                    "m7": 5,
                    "m7add11": 5,
                    "m7add13": 5,
                    "m7b5": 5,
                    "m7b9": 5,
                    "m9": 5,
                    "m9b5": 5,
                    "m9-Maj7": 5,
                    "madd9": 5,
                    "Maj11": 5,
                    "Maj13": 5,
                    "Maj7": 5,
                    "Maj7#11": 5,
                    "Maj7#5": 5,
                    "Maj7add13": 5,
                    "Maj7b5": 5,
                    "Maj9": 5,
                    "Maj9#11": 5,
                    "Maj9#5": 5,
                    "Maj9su4": 5,
                    "Majb5": 5,
                    "Major": 5,
                    "mb5": 5,
                    "minor": 5,
                    "m-Maj11": 5,
                    "m-Maj13": 5,
                    "m-Maj7": 5,
                    "m-Maj7add11": 5,
                    "m-Maj7add13": 5,
                    "sus2": 5,
                    "sus4": 5,
                    "tri": 5
                },
                "feels": {
                    "Glitchy": 1,
                    "Swirling": 2,
                    "Staccato": 3,
                    "Binaural": 3,
                    "Rubato": 4,
                    "Legato": 5
                },
                "genres": {
                    "Ska": 1,
                    "Pop": 2,
                    "Space Glam Rock": 3,
                    "Spaghetti Western": 4,
                    "Drum n Bass": 5,
                    "Not Ska": 5
                },
                "influences": {
                    "Mariah Carey": 1,
                    "U2": 2,
                    "OutKast": 3,
                    "Tim Hecker": 4,
                    "Sufjan Stevens": 4
                },
                "instruments": {
                    "Guitar": 4,
                    "Piano": 3,
                    "Violin": 3,
                    "Daxophone": 5
                },
                "key-signatures": {
                    "roots": {
                        "C": 5,
                        "C#": 5,
                        "D": 5,
                        "D#": 5,
                        "E": 5,
                        "F": 5,
                        "F#": 5,
                        "G": 5,
                        "G#": 5,
                        "A": 5,
                        "A#": 5,
                        "B": 5
                    },
                    "modes": {
                        "mild": {
                            "Ionian": 5,
                            "Dorian": 5,
                            "Phrygian": 5,
                            "Lydian": 5,
                            "Mixolydian": 5,
                            "Aeolian": 5,
                            "Locrian": 5
                        },
                        "spicy": {
                            "Major Bebop": 5,
                            "Major Pentatonic": 4,
                            "Minor Harmonic": 4,
                            "Minor Hungarian": 3,
                            "Minor Melodic": 5,
                            "Minor Neapolitan": 3,
                            "Minor Pentatonic": 3,
                            "Arabic": 2,
                            "Blues": 3,
                            "Diminished": 2,
                            "Dominant Bebop": 3,
                            "Enigmatic": 1,
                            "Neapolitan": 1,
                            "Insen": 2,
                            "Whole Tone": 2
                        }
                    },
                    "generic": {
                        "0 sharps/flats": 5,
                        "1 sharp": 5,
                        "2 sharps": 5,
                        "3 sharps": 5,
                        "4 sharps": 5,
                        "5 sharps": 5,
                        "6 sharps": 5,
                        "1 flat": 5,
                        "2 flats": 5,
                        "3 flats": 5,
                        "4 flats": 5,
                        "5 flats": 5
                    }
                },
                "moods": {
                    "Stoned": 1,
                    "Confused": 2,
                    "Stressed Out": 3,
                    "Sociopolitic Fervor": 4,
                    "Hopeful": 5,
                    "Optimistic": 5
                },
                "themes": {
                    "Western": 3,
                    "Horror": 5,
                    "Oriental": 3,
                    "Celtic": 5,
                    "Alpine": 3,
                    "Mediterranean": 3,
                    "Middle-Eastern": 3,
                    "African": 3,
                    "Scandinavian": 3,
                    "Slavic": 3,
                    "Baltic": 3,
                    "Gypsy": 3,
                    "Mexican": 2,
                    "European Renaissance": 4,
                    "Gangster": 3,
                    "Vice": 2
                },
                "time-signatures": {
                    "numerator": {
                        "2":  2,
                        "3":  5,
                        "4":  5,
                        "5":  3,
                        "6":  3,
                        "7":  4,
                        "8":  2,
                        "9":  3,
                        "10": 1,
                        "11": 1,
                        "12": 1,
                        "13": 1,
                        "14": 1,
                        "15": 1
                    },
                    "denominator": {
                        "2":  2,
                        "4":  5,
                        "8":  2,
                        "16": 1
                    }
                }
            }
            request.session.save()
        field_data = request.session["metadata"]["user_data"].get(field_name, {"Sample Field": "Enter Your Frequency Here! (1-5)"})
        context = {
            "field_name": field_name,
            "field_data": field_data,
            "depth": get_dict_depth(field_data)
        }
        return render(request, "pages/config.html", context=context)
    else:
        db = connect_to_database()
        user_id = request.session["metadata"]["id"]
        if db["user_data"].find({"id": user_id}).count() == 0:
            raise Exception(f"An unexpected error occurred: the user_data dict for user id {user_id} not found in database!")
        if field_name not in request.session["metadata"]["user_data"]:
            request.session["metadata"]["user_data"][field_name] = {}
        db["user_data"].update_one({"id": user_id}, {"$set": {f'user_data.scaffold_config.{field_name}': request.session["metadata"]["user_data"][field_name]}})
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
    request.session["metadata"]["user_data"][field_name] = new_field_data
    request.session.save()
    return redirect('pages:index')


@login_required
def delete(request, data_id):
    print(data_id)
    data_id_split = data_id.replace("-over-", "/").replace("-space-", " ").split("-")
    try:
        if len(data_id_split) == 2:
            del request.session["metadata"]["user_data"][data_id_split[0]][data_id_split[1]]
        elif len(data_id_split) == 3:
            del request.session["metadata"]["user_data"][data_id_split[0]][data_id_split[1]][data_id_split[2]]
        elif len(data_id_split) == 4:
            del request.session["metadata"]["user_data"][data_id_split[0]][data_id_split[1]][data_id_split[2]][data_id_split[3]]
        request.session.save()
    except:
        pass
    finally:
        return redirect('field:config', data_id_split[0])