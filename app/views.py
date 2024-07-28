from django.shortcuts import render
from django.http import HttpResponse

from tests.models import Tests

def index(request):
    context = {
        "title":"Сайт говно",
        "description":"Педелывай",
        "testes": Tests.objects.all()
    }
    return render(request, "app/index.html", context=context)


def about(request):
    return render(request, "app/about.html")
