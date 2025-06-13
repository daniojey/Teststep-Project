from datetime import datetime
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView, View
import requests

from tests.models import TestResult, Tests, TestsReviews
from users.models import User, UsersGroupMembership

class IndexView(LoginRequiredMixin, TemplateView):
    """
    View to render the main index page for logged-in users.

    This view displays tests associated with the current user, grouped into
    categories such as completed tests, uncompleted tests, and tests awaitin review.
    It also provides information about the user's group memebership.

    
    Attributes
    ----------
    template_name : str
        The path to the template user for renedering the index page.

    
    Methods
    -------
    get_context_data(**kwargs)
        Adds custom context data for the template, including tests categorized
        by their status(completed, uncompleted, or awaiting review) and the user`s group
    """
    template_name = 'app/index.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and add context data for the index page

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments passed to the view

        Returns
        -------
        dict
            A dictionary containing the following keys:
            - 'tests' : QuerySet of all test associated with the user.
            - 'uncompleted_tests' : QuerySet of tests the user has not completed.
            - 'awaitig_tests' : QuerySet of tests awaiting teacher review.
            - 'completed_tests' : QuerySet of tests the user has completed.
            - 'group' : str or Group
                The name of the user`s group, or 'Без группы' if the user not in a group
        
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user  # Используем существующий объект user
        user_id = str(user.id)

        # Получаем группу одним запросом с select_related
        group_membership = UsersGroupMembership.objects.select_related('group').filter(user=user).first()
        group = group_membership.group if group_membership else "Без групи"

        # Получаем все нужные test_id одним запросом
        completed_test_ids = set(TestResult.objects.filter(user=user).values_list('test_id', flat=True))
        awaiting_test_ids = set(TestsReviews.objects.filter(user=user).values_list('test_id', flat=True))

        # Получаем дату и время сервера
        server_time = timezone.make_aware(datetime.now(), timezone.get_default_timezone())

        # Получаем все тесты одним запросом
        all_tests = (Tests.objects
                    .filter(students__students__contains=[user_id])
                    .order_by('-date_taken'))
        
        # Используем Python для фильтрации вместо дополнительных запросов к БД
        tests_dict = {test.id: test for test in all_tests}
        actual_test_dict = {test.id: test for test in all_tests.filter(Q(date_in__lt=server_time) & Q(date_out__gte=server_time))}
        
        uncompleted_tests = [
            test for test_id, test in actual_test_dict.items()
            if test_id not in completed_test_ids and test_id not in awaiting_test_ids
        ]
        
        awaiting_tests = [
            test for test_id, test in tests_dict.items()
            if test_id in awaiting_test_ids
        ]
        
        completed_tests = [
            test for test_id, test in tests_dict.items()
            if test_id in completed_test_ids
        ]

        context.update({
            'tests': all_tests,
            'uncompleted_tests': uncompleted_tests,
            'awaiting_tests': awaiting_tests,
            'completed_tests': completed_tests,
            'group': group,
        })

        return context

class AboutDevView(TemplateView):
    template_name = 'app/about_dev.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        dev_name = 'daniojey'
        url = f"https://api.github.com/users/{dev_name}"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            context['github_user'] = {
                "image": data["avatar_url"],
                'bio': data["bio"],
                'github_url': data['html_url'],
                'dev_projects': data['public_repos']
            }

        return context
    

# @login_required
# def index(request):
#     user_id = str(request.user.id)  # Получаем ID текущего пользователя
#     user = get_object_or_404(User, id=request.user.id)

#     # Получаем группу пользователя
#     if UsersGroupMembership.objects.filter(user=user).exists():
#         group = UsersGroupMembership.objects.filter(user=user).first()
#         group = group.group
#     else:
#         group = "Без группы"



#     # Фильтруем тесты, где поле students содержит ID текущего пользователя
#     tests = Tests.objects.filter(students__students__contains=[user_id]).order_by('-date_taken')

#     # Завершенные тесты
#     completed_tests = TestResult.objects.filter(user=user).values_list("test_id", flat=True)

#     # Тесты ожидающие проверку
#     awaiting_tests = TestsReviews.objects.filter(user=user).values_list("test_id", flat=True)

#     # Тесты ожидающие прохождения
#     uncompleted_tests = tests.exclude(id__in=completed_tests).exclude(id__in=awaiting_tests)


#     context = {
#         "tests": tests,
#         "uncompeted_tests": uncompleted_tests,
#         "awaiting_tests": tests.filter(id__in=awaiting_tests),
#         "completed_tests": tests.filter(id__in=completed_tests),
#         "group": group
#     }
#     return render(request, "app/index.html", context=context)


class CspReports(TemplateView):

    def get(self, request, *args, **kwargs):
        print('CSP report received')
        return HttpResponse(status=200)
    
    def post(self, request, *args, **kwargs):
        print('CSP report received')
        return HttpResponse(status=200)
    
