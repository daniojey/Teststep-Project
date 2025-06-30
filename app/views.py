from datetime import datetime
import pprint
from django.db.models import Q, Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView, View
import requests

from tests.models import TestResult, Tests, TestsReviews
from users.models import Group, User

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
        context = super().get_context_data(**kwargs)
        user = self.request.user  # Используем существующий объект user
        user_id = str(user.id)

        server_time = timezone.make_aware(datetime.now(), timezone.get_default_timezone())

        groups = user.group.prefetch_related(
            Prefetch(
                'test_group',
                queryset=Tests.objects.filter(
                    students__id=user_id
                ).select_related('group'),
                to_attr='all_group_tests'
            ),

            Prefetch(
                'test_reviews',
                queryset=TestsReviews.objects.filter(
                    user_id=user_id
                ).select_related(
                    'test', 'user'
                ).only(
                    'test', 'group', 'user'
                ),
                to_attr="test_reviews_in_group"
            ),

            Prefetch(
                'test_results',
                queryset=TestResult.objects.filter(
                    user_id=user_id
                ).select_related(
                    'test'
                ).only(
                    'test', 'group'
                ),
                to_attr='test_results_in_group'
            )
        ).all()

        groups_data = {}

        for i, group in enumerate(groups):
            group_dict = {}

            group_dict['group_name'] = group.name
            
            all_tests = group.all_group_tests
            active_tests = [
                test for test in all_tests
                if test.date_in < server_time and test.date_out >= server_time
            ]

            all_test_ids = {test.id for test in all_tests}
            active_tests_ids = {test.id for test in active_tests}


            test_reviews = [
                tr for tr in group.test_reviews_in_group
            ]
            test_reviews_ids = {item.test_id for item in test_reviews}
            group_dict['test_reviews'] = [item.test for item in test_reviews]


            test_results = [
                tr for tr in group.test_results_in_group if tr.test_id in active_tests_ids
            ]
            test_results_ids ={item.test_id for item in test_results}
            group_dict['test_results'] = [item.test for item in test_results]


            exclude_ids = test_results_ids | test_reviews_ids
            results_ids = list(set(all_test_ids) - exclude_ids)

            uncomplete_tests = [test for test in active_tests if test.id in results_ids]
            group_dict['uncomplete_tests'] = uncomplete_tests


            groups_data[f"Group {i}"] = group_dict


        
        context.update({"group_data": groups_data})

            

        # Получаем группу одним запросом с select_related
        # group_membership = UsersGroupMembership.objects.select_related('group').filter(user=user).first()
        # group = group_membership.group if group_membership else "Без групи"

        # # Получаем все нужные test_id одним запросом
        # completed_test_ids = set(TestResult.objects.filter(user=user).values_list('test_id', flat=True))
        # awaiting_test_ids = set(TestsReviews.objects.filter(user=user).values_list('test_id', flat=True))

        # # Получаем дату и время сервера
        # server_time = timezone.make_aware(datetime.now(), timezone.get_default_timezone())

        # # Получаем все тесты одним запросом
        # all_tests = (Tests.objects
        #             .filter(students__students__contains=[user_id])
        #             .order_by('-date_taken'))
        
        # # Используем Python для фильтрации вместо дополнительных запросов к БД
        # tests_dict = {test.id: test for test in all_tests}
        # actual_test_dict = {test.id: test for test in all_tests.filter(Q(date_in__lt=server_time) & Q(date_out__gte=server_time))}
        
        # uncompleted_tests = [
        #     test for test_id, test in actual_test_dict.items()
        #     if test_id not in completed_test_ids and test_id not in awaiting_test_ids
        # ]
        
        # awaiting_tests = [
        #     test for test_id, test in tests_dict.items()
        #     if test_id in awaiting_test_ids
        # ]
        
        # completed_tests = [
        #     test for test_id, test in tests_dict.items()
        #     if test_id in completed_test_ids
        # ]

        # context.update({
        #     'tests': all_tests,
        #     'uncompleted_tests': uncompleted_tests,
        #     'awaiting_tests': awaiting_tests,
        #     'completed_tests': completed_tests,
        #     'group': group,
        # })

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
    
