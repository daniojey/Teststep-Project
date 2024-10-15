from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from tests.models import TestResult, Tests, TestsReviews
from users.models import User, UsersGroupMembership


@login_required
def index(request):
    user_id = str(request.user.id)  # Получаем ID текущего пользователя
    user = get_object_or_404(User, id=request.user.id)

    # Получаем группу пользователя
    if UsersGroupMembership.objects.filter(user=user).exists():
        group = UsersGroupMembership.objects.filter(user=user).first()
        group = group.group
    else:
        group = "Без группы"



    # Фильтруем тесты, где поле students содержит ID текущего пользователя
    tests = Tests.objects.filter(students__students__contains=[user_id]).order_by('-date_taken')

    # Завершенные тесты
    completed_tests = TestResult.objects.filter(user=user).values_list("test_id", flat=True)

    # Тесты ожидающие проверку
    awaiting_tests = TestsReviews.objects.filter(user=user).values_list("test_id", flat=True)

    # Тесты ожидающие прохождения
    uncompleted_tests = tests.exclude(id__in=completed_tests).exclude(id__in=awaiting_tests)


    context = {
        "tests": tests,
        "uncompeted_tests": uncompleted_tests,
        "awaiting_tests": tests.filter(id__in=awaiting_tests),
        "completed_tests": tests.filter(id__in=completed_tests),
        "group": group
    }
    return render(request, "app/index.html", context=context)

def about(request):
    return render(request, "app/about.html")
