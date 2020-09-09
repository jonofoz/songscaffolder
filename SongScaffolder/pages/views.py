from django.shortcuts import render

# Create your views here.
def index(request):

    context = {
        "fields": []
    }

    for field_title, *_, field_info in [
        ("Chords", "Checking this will include random chords into the scaffold. These chords are are specified by clicking the respective list icon."),
        ("Feels", ""),
        ("Genres", ""),
        ("Influences", ""),
        ("Instruments", ""),
        ("Key Signatures", ""),
        ("Moods", ""),
        ("Themes", ""),
        ("Time Signatures", ""),
    ]:
        context["fields"].append ({
            "title": field_title,
            "id": field_title.replace(" ","-").lower(),
            "info": field_info
        })
    return render(request, 'pages/index.html', context=context)