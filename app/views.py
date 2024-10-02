from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from tests.models import Tests
from users.models import User


@login_required
def index(request):
    user_id = str(request.user.id)  # Получаем ID текущего пользователя

    # Фильтруем тесты, где поле students содержит ID текущего пользователя
    tests = Tests.objects.filter(students__students__contains=[user_id]).order_by('-date_taken')

    context = {
        "tests": tests,
    }
    return render(request, "app/index.html", context=context)

def about(request):
    return render(request, "app/about.html")
