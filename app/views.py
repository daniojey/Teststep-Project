from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from tests.models import Tests

@login_required
def index(request):
    tests = Tests.objects.all().order_by('-date_taken')
    context = {
        "tests" : tests,
    }
    return render(request, "app/index.html", context=context)


def about(request):
    return render(request, "app/about.html")
