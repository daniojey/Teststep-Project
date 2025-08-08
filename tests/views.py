# tests/views.py
# Базовые библиотеки
from copyreg import constructor
from decimal import Decimal
import json
from multiprocessing import Value
import os
from pprint import pprint
import random
import base64
from datetime import datetime, timedelta
from unicodedata import category
from wsgiref.util import request_uri

# Импортируем библиотеки Django
from django.utils import timezone
from django.views.generic import FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.db.models import F, ExpressionWrapper, Prefetch, Sum, fields
from django.forms import ClearableFileInput, DateInput, DateTimeInput, NumberInput, TextInput, Textarea
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.utils.timezone import localtime, now
from django.urls import reverse, reverse_lazy
from django.core.files.base import ContentFile
from django.views import View

# Библиотеки проекта
from common.mixins import CacheMixin
from main.settings import ENABLE_CELERY, ENABLE_REDIS
from tests.permissions import TestcheckOwnerOrAdminMixin, CheckPersonalMixin
from tests.services.take_test_review_service import TakeTestReviewService
from tests.services.take_test_service import TakeTestService
from tests.services.test_results_service import TestResultsService
from tests.tasks import send_emails_task
from tests.utils import check_min_datetime, send_emails_from_users
from users.models import Group, User
from .models import Categories, MatchingPair, QuestionGroup, TestResult, Tests, Question, Answer, TestsReviews
from .forms import MatchingPairForm, QuestionGroupForm, QuestionStudentsForm, TestForm, QuestionForm, AnswerForm, TestReviewForm, TestTakeForm


def index(request):
    return render(request, 'tests/index.html')


class UserRatingView(LoginRequiredMixin, TemplateView):
    template_name = 'tests/rating.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        is_special_user = user.is_staff or user.is_superuser or user.teacher


        if is_special_user:
            groups = user.group.prefetch_related(
                Prefetch(
                    'test_group',
                    queryset=Tests.objects.select_related('user'),
                    to_attr='tests_for_user'
                )
            )

            # group_data = {}

            # for i, group in enumerate(groups):
            #     group_dict = {}

            #     group_dict['group_name'] = group.name

            #     group_dict['tests'] = [test for test in group.tests_for_user]

            #     group_data[f"Group {i}"] = group_dict

            group_data = {
                f'Group {i}': {
                    'group_name': group.name,
                    'tests': list(group.tests_for_user)
                }

                for i, group in enumerate(groups)
            }
            

            pprint(group_data)

        else:
            groups = user.group.prefetch_related(
                Prefetch(
                    'test_results',
                    queryset=TestResult.objects.select_related(
                        'test', 'user'
                        ).filter(
                            user=user
                        ).only(
                            'test', 'user', 'group'
                    ),
                    to_attr='test_results_group'
                )
            ).all()

            # group_data = {}

            # for i, group in enumerate(groups):
            #     group_dict = {}

            #     group_dict['group_name'] = group.name

            #     group_dict['tests'] = [item.test for item in group.test_results_group]

            #     group_data[f"Group {i}"] = group_dict

            for group in groups:
                print([ result.user for result in group.test_results_group])

            group_data = {
                f"Group {i}": {
                    'group_name': group.name,
                    'tests': [result.test for result in group.test_results_group],
                }

                for i, group in enumerate(groups)
            }


            pprint(group_data)        
        
        # # Проверка на принадлежность к группе и статус учителя
        # membership = UsersGroupMembership.objects.select_related('group').filter(user=user).first()
        # if membership and membership.owner:
        #     # Пользователь - учитель группы, выводим тесты, которые он выгружал
        #     context['tests'] = Tests.objects.filter(user=user)  # Все тесты, созданные учителем
        # else:
        #     # Пользователь - студент, выводим его результаты
        #     test_lists = TestResult.objects.filter(user=user).values_list("test_id", flat=True)
        #     context['tests'] = Tests.objects.filter(id__in=test_lists)  # Тесты, по которым есть результаты у студента

        
            

        context.update({
        #     'group': membership.group if membership and membership.group else None,
            "groups": group_data, 
            'active_tab': 'rating',
        })

        return context



class RatingTestView(LoginRequiredMixin, TemplateView):
    template_name = "tests/rating_test.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # user = self.request.user
        test_id = self.kwargs.get('test_id')

        try:
            test_group_id, test_name = Tests.objects.filter(id=test_id).values_list('group_id', 'name').first()
        except TypeError:
            raise Http404("Poll does not exist")
        except Tests.DoesNotExist:
            raise Http404("Poll does not exist")
        
        data = Group.objects.filter(id=test_group_id).prefetch_related(
            Prefetch(
                'test_results',
                queryset=TestResult.objects.filter(
                    test__id=test_id
                ).select_related(
                    'test', 'user'
                ).annotate(
                    scores=F('score'),
                    duration_seconds=ExpressionWrapper(F('duration'), output_field=fields.DurationField())
                ).order_by('-scores', 'duration_seconds'),
                to_attr='test_results_data'
            )
        ).first()

        context.update({
            'results': data.test_results_data,
            'active_tab': 'rating',
            'test_name': test_name
        })

        return context



class AllTestsView(LoginRequiredMixin,CheckPersonalMixin, TemplateView):
    template_name = "tests/all_tests.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category = self.request.GET.get('category', None)
        search = self.request.GET.get('search', None)

        page = self.request.GET.get('page', 1)
        page_size = 10

        categories = Categories.objects.all()

        # Если админ то отображаем все тесты, иначе только тесты текущего пользователя
        if self.request.user.is_superuser:
            tests = Tests.objects.all().order_by('-date_taken')

            if category:
                category_filter = Categories.objects.get(name=category)
                print(category_filter)
                tests = tests.filter(category=category_filter)
            
            if search:
                tests = tests.filter(name__icontains=search)

        else:
            tests = Tests.objects.filter(user=self.request.user).order_by('-date_taken')

            if category:
                category_filter = Categories.objects.get(name=category)
                print(category_filter)
                tests = tests.filter(category=category_filter)
            
            if search:
                tests = tests.filter(name__icontains=search)


        paginator = Paginator(tests, page_size)

        page_obj = paginator.get_page(page)

        context.update({
            'page_obj': page_obj,
            'tests': tests,
            'active_tab': 'my_tests',
            'paginate_active': True if paginator.count > page_size else None,
            'categories': categories 
        })

        return context



class CreateTestView(LoginRequiredMixin,CheckPersonalMixin, FormView):
    template_name = 'tests/create_test.html'
    form_class = TestForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Связываем форму с переменной но без сохранения в БД
        test = form.save(commit=False)
        test.user = self.request.user

        # Получаем время на прохождение из кастомного поля формы
        test.duration = form.cleaned_data.get('raw_duration')
        test.save()

        self.object = test
        return super().form_valid(form)

    def form_invalid(self, form):
        """ Если форма не валидна то собераем все ошибки и рендерим их в шаблон """
        errors = []

        if form.non_field_errors():
            errors.extend(form.non_field_errors())

        for field, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(f"- {error}")

        return self.render_to_response({
            'form': form,
            'errors': errors, 
            'detail_errors': {
                key: value
                for key, value in form.errors.items()
            }
            })
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Доабвление active_tab необходимо для правильной работы стилей ссылок в header 
        context['active_tab'] = 'create'
        return context
    
    def get_success_url(self) -> str:
        return reverse('tests:add_questions', kwargs={'test_id': self.object.id})
    


class EditTestView(LoginRequiredMixin,CheckPersonalMixin, UpdateView):
    model=Tests
    template_name = "tests/edit_test.html"
    fields = ['name', 'description','image', 'duration', 'date_in','date_out', 'category', 'check_type']

    def form_valid(self, form):
        #Модифицируем время
        duration = form.cleaned_data.get('duration')
        if duration is not None and isinstance(duration, timedelta):
            form.instance.duration = timedelta(minutes=int(duration.total_seconds()))
        else:
            form.add_error('duration', 'Невірний формат часу на проходження тесту')
            return super().form_invalid(form)
            
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        test_id = self.kwargs.get('pk')
        test = Tests.objects.get(id=test_id)

        context.update({
            'test': test
        })

        return context
    
    def get_form(self, form_class = None):
        """Что делаем:
        1. Получаем форму
        2. Делаем необходимое количество строк в поле description через attrs
        3. Убираем картинку из предзаполнения формы
        4. Добавляем класс, id, и текст для поля image
        5. Добавляем список категорий исключая базовый пустой вариант виджета
        6. Добавляем класс и тип для виджета date_out
        7. Присваиваем date-out локальное отображение даты сервера
        """

        form = super().get_form(form_class)

        form.fields['description'].widget = Textarea(attrs={'rows': 4})
        form.initial['image'] = None
        form.fields['image'].widget = ClearableFileInput(attrs={
            'class': 'form-image-field',
            'data-no-file-text': 'Оберіть фото',  
            'id': 'uploadImage'
        })

        form.fields['duration'].widget = TextInput(attrs={'id':'durationField', "placeholder": 'Введіть тривалість тесту в хвилинах'})
        form.initial['duration'] = int(self.object.duration.total_seconds() / 60)

        form.fields['category'].choices = [(item.id, item.name) for item in Categories.objects.all()]

        form.fields['date_in'].widget = DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control',  # опционально (для стилизации)
                'min': check_min_datetime(localtime(self.object.date_in), localtime())
            },
            format='%Y-%m-%dT%H:%M'     # обязательный формат
        )

        form.fields['date_out'].widget = DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control',  # опционально (для стилизации)
                'min': check_min_datetime(localtime(self.object.date_in), localtime())
            },
            format='%Y-%m-%dT%H:%M'     # обязательный формат
        )

        if self.object.date_in:
            local_date = localtime(self.object.date_in)
            form.initial['date_in'] = local_date.strftime('%Y-%m-%dT%H:%M')

        if self.object.date_out:
            local_date = localtime(self.object.date_out)
            print("LOCAL DATETIME",local_date)
            form.initial['date_out'] = local_date.strftime('%Y-%m-%dT%H:%M')
        return form
    
    def get_success_url(self):
        return reverse_lazy('tests:add_questions', kwargs={'test_id': self.object.id})



class DeleteTestView(TestcheckOwnerOrAdminMixin, View):
    def post(self, request, *args, **kwargs):
        test_id = kwargs.get('test_id', None)
        if not test_id:
            return Http404('Not found test')
        
        test = get_object_or_404(Tests, id=test_id)
        test.delete()

        return redirect(reverse_lazy('app:index'))



class AddQuestionGroupView(LoginRequiredMixin,TestcheckOwnerOrAdminMixin, FormView):
    template_name = 'tests/adq.html'
    form_class = QuestionGroupForm

    def form_valid(self, form):
        test_id = self.kwargs.get('test_id')
        test = get_object_or_404(Tests, id=test_id)

        # Присваеваем группу вопросов к тесту
        question_group = form.save(commit=False)
        question_group.test = test
        question_group.save()

        return redirect("tests:add_questions",  test_id=test.id)
    


class AddQuestionsView(LoginRequiredMixin,TestcheckOwnerOrAdminMixin, TemplateView):
    template_name = 'tests/add_questions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        test_id = self.kwargs.get('test_id')

        # Получаем тест и пользователя
        test = get_object_or_404(Tests.objects.select_related('user'), id=test_id)
        user = self.request.user

        # Получаем все вопросы теста и связанные с ними группы
        questions = Question.objects.filter(test=test).select_related('group')

        # Получаем все группы вопросов, связанные с тестом, и предзагружаем их вопросы
        question_groups = list(
            QuestionGroup.objects.filter(test=test).prefetch_related(
                Prefetch('questions_group', queryset=questions)
            )
        )
        
        # Получаем все вопросы, которые не пренадлежат ни одной из груп
        ungrouped_questions = list(questions.filter(group__isnull=True))

        # Инициализируем формы
        question_form = QuestionForm(test=test)
        form_student = QuestionStudentsForm(test=test, user=user)


        context.update({
            'test': test,
            'question_groups': question_groups,
            'ungrouped_questions': ungrouped_questions,
            'question_form': question_form,
            'form_student': form_student,
        })

        return context

    def post(self, request, *args, **kwargs):
        print(request.POST)
        test_id = self.kwargs.get('test_id')
        test = get_object_or_404(Tests, id=test_id)
        user = request.user

        # Получаем тип формы из POST-запроса
        form_type = request.POST.get('form_type')

        # Получаем формы и передаем в них тест, пользователя и данные запроса
        question_form = QuestionForm(request.POST, request.FILES, test=test)
        students_form = QuestionStudentsForm(request.POST, request.FILES, test=test, user=user)

        # Если в запросе попытка добавить вопрос то обрабатываем его
        if form_type == 'form_question':
            if question_form.is_valid():
                question = question_form.save(commit=False)
                question.test = test
                question.save()
                return redirect('tests:add_questions', test_id=test.id)
            else:
                # Если форма не валидна, собираем ошибки и рендерим их в шаблон
                errors = []

                if question_form.non_field_errors():
                    errors.extend(question_form.non_field_errors())

                for field, field_errors in question_form.errors.items():
                    for error in field_errors:
                        errors.append(f"- {error}")

                context = self.get_context_data(test_id=kwargs.get('test_id'))
                context['form_question'] = question_form
                context['errors'] = errors
            
                return self.render_to_response(context)
        
        # Если в запросе попытка добавить студентов то обрабатываем его
        elif form_type == 'form_student':
            # Если форма валидна, то получаем спасок всех студентов и сохраняем в одноименнованное поле в модели Tests
            if students_form.is_valid():
                data_users = students_form.cleaned_data.get('students')
                form_users = set((int(ids) for ids in data_users))
                test_students = set(test.students.all().values_list("id", flat=True))
                
                # Получаем как пользователей которых нужно удалить так и тех которых нужно будет добавить 
                remove_set = test_students.difference(form_users)
                add_set = form_users.difference(test_students)

                if add_set:
                    test.students.add(*add_set)

                if remove_set:
                    test.students.remove(*remove_set)

                test.save()

                if ENABLE_CELERY == 'True' and ENABLE_REDIS == 'True':
                    send_emails_task.delay(data_users, test.id)
                else:
                    send_emails_from_users(data_users, test)

                return JsonResponse({'status': 'success', 'message': 'Студенты обновлены.'}, status=202)
            else:
                return JsonResponse({'status': 'error', 'message': 'Opps, помилка'}, status=400)
            
        
        context = self.get_context_data()
        context['question_form'] = question_form
        context['form_students'] = students_form
        return self.render_to_response(context)



class DeleteQuestionView(LoginRequiredMixin, CheckPersonalMixin, View):
    def post(self, request, *args, **kwargs):
        question_id = kwargs.get('question_id', None)
        if not question_id:
            return Http404('Question not found')

        question = get_object_or_404(Question.objects.select_related('test'), id=question_id)
        
        test = question.test
        question.delete()

        return redirect('tests:add_questions', test_id=test.id)



def complete_questions(request, test_id):
    return redirect('app:index')



class AddAnswersView(LoginRequiredMixin,CheckPersonalMixin, FormView):
    template_name = 'tests/add_answer.html'
    form_class = AnswerForm

    def form_valid(self, form):
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=question_id)

        # Связываем форму с переменной но без сохранения в БД после чего присваиваем ответ к вопросу
        answer = form.save(commit=False)
        answer.question = question
        answer.save()

        if question.answer_type == "INP":
            question.update_question_score()

        # print("КОЛ_ВО очков",total_score)
        return redirect('tests:add_answers', question_id=question.id)
    
    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """ Получаем вопрос а также все его ответы и его группу"""
        context = super().get_context_data(**kwargs)
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(
            Question.objects.select_related('test', 'group').prefetch_related('answers'),
            id=question_id)
        
        answers = question.answers.all()
        question_group = question.group
        
        # test = question.test
        # questions = test.questions.all()

        context.update({
            'question': question,
            # 'test': test,
            # 'questions': questions,
            'group': question_group,
            'answers': answers,
            'form_type': 'Ответ',
            'action_url': 'tests:add_answers'
        })

        return context



class SaveCorrectView(View):
    def post(self, request, *args, **kwargs):
        # Получаем ID вопроса из URL и для вопроса предзагружаем все ответы
        question = get_object_or_404(Question.objects.prefetch_related('answers'), id=self.kwargs['question_id'])

        # Получаем список ID для сохранения ответов из запроса
        correct_answers_ids = request.POST.getlist('correct_answers')

        # Обрабатываем лишь случаи вопросов с одиночным выбором и множественным выбором, остальные не изменяем
        if question.answer_type == 'SC':

            if correct_answers_ids:

                # Все ответі делаем не верными
                question.answers.all().update(is_correct=False)

                # Получаем ID первого ответа из списка и сохраняем его как верный
                id_answer = correct_answers_ids[0]
                answer = Answer.objects.filter(id=id_answer).update(is_correct=True)

                question.update_question_score()
            
        elif question.answer_type == 'MC':
             
             if correct_answers_ids:
                # Все ответі делаем не верными после чего делаем верными только те которые которых ID совпадают с ID из списка
                question.answers.all().update(is_correct=False)
                answers = Answer.objects.filter(id__in=correct_answers_ids).update(is_correct=True)

                question.update_question_score()
        
        elif question.answer_type == 'INP':
            question.update_question_score()

        else:

            # Остальные случаи игнорируем
            ...

        return redirect(reverse('tests:add_questions', args=[question.test.id]))
    


class DeleteAnswerView(CheckPersonalMixin, View):
    def post(self, request, *args, **kwargs):
        answer_id = kwargs.get('answer_id', None)
        if not answer_id:
            Http404('Answer not found')

        answer = get_object_or_404(Answer.objects.select_related('question'), id=answer_id)
        question = answer.question

        answer.delete()
        return redirect('tests:add_answers', question_id=question.id)



class AddMathicngPairView(LoginRequiredMixin, CheckPersonalMixin, FormView):
    template_name = 'tests/add_answer.html'
    form_class = MatchingPairForm

    def form_valid(self, form):
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=question_id)

        # Присваиваем форму переменной но без сохранения в БД после чего присваиваем ответ к вопросу
        answer = form.save(commit=False)
        answer.question = question
        answer.save()

        question.update_question_score()
        return redirect('tests:add_matching_pair', question_id=question.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_id = self.kwargs.get('question_id')

        # Получаем вопрос а также все его ответы и его группу
        question = get_object_or_404(
            Question.objects.select_related('test').prefetch_related('test__questions', 'answers', 'matching_pairs'),
            id=question_id
        )

        # matching_pairs = MatchingPair.objects.filter(question=question)


        context.update({
            'question': question,
            'group': question.group,
            'form_type': 'Соотвецтвие',
            'action_url': 'tests:add_matching_pair'
        })

        return context



class DeleteMatchingPairView(CheckPersonalMixin, View):
    def post(self, request, *args, **kwargs):
        matching_pair_id = kwargs.get('pair_id', None)
        if not matching_pair_id:
            Http404('Mathing pair not found')

        matching_pair = get_object_or_404(MatchingPair.objects.select_related('question'), id=matching_pair_id)
        question = matching_pair.question
        matching_pair.delete()
        return redirect('tests:add_matching_pair', question_id=question.id)



class ChangeQuestionScoreView(View):
    def post(self, request, ids=None, *args, **kwargs):
        if ids:
            post_scores = request.POST.get('score')

            try:
                score = float(post_scores)
            except ValueError as e:
                return JsonResponse({'error': 'Помилка при обробці балів', 'detail': f"{e}"}, status=400)
            
            try:
                question = get_object_or_404(Question, id=ids)
                question.scores = score
                question.save()
            
                return JsonResponse({"success": f"Бали змінено на {score}"})
            except Exception as e:
                return JsonResponse({'error': 'Помилка при обробці відповіді', 'detail': f"{e}"}, status=400)



class ChangeAnswerScoreView(View):

    def post(self, request, ids=None, *args, **kwargs):
        if ids:
            type_answer = request.POST.get('type')
            post_scores = request.POST.get('score')
            print(post_scores)

            try:
                score = float(post_scores)
            except ValueError as e:
                return JsonResponse({'error': 'Помилка при обробці балів', 'detail': f"{e}"}, status=400)


            if type_answer == "Matching":

                try:
                    matching_pair = MatchingPair.objects.get(id=ids)
                    matching_pair.score = score
                    matching_pair.save()

                    matching_pair.question.update_question_score()

                    return JsonResponse({"success": f"Бали змінено на {score}"})
                except Exception as e:
                    return JsonResponse({'error': 'Помилка при обробці відповіді', 'detail': f"{e}"}, status=400)
                

            elif type_answer == 'Answer':

                try:
                    answer = Answer.objects.get(id=ids)
                    answer.score = score
                    answer.save()

                    answer.question.update_question_score()

                    return JsonResponse({"success": f"Бали змінено на {score}"})
                except Exception as e:
                    return JsonResponse({'error': 'Помилка при обробці відповіді', 'detail': f"{e}"}, status=400)
                
            return JsonResponse({'error': 'Помилка обробки відповіді'})



class TestPreviewView(LoginRequiredMixin,TemplateView):
    template_name = 'tests/test_preview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        test_id = self.kwargs.get('test_id')


        # Получаем тест и результат по тесту либо то что тест находится на ожидании проверки, необходимо для отображения стилей
        test = get_object_or_404(Tests.objects.select_related('user'), id=test_id)

        server_time = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
        test_date_in = localtime(test.date_in)
        test_date_out = localtime(test.date_out)

        if server_time > test_date_in and server_time < test_date_out:
            # print('Вермя сервера меньше', server_time)
            # print('Время теста', test_date_in)
            # print('Вермя окончания теста', test_date_out)
            open_test = True
        else:
            open_test = False

        test_results = TestResult.objects.filter(test=test, user=user).select_related('test', 'user').first()
        test_review = TestsReviews.objects.filter(user=user, test=test).exists()

        context.update({
            'test': test,
            'test_results': test_results,
            'test_review': test_review,
            'open_test': open_test
        })

        return context
    


class TakeTestView(LoginRequiredMixin ,FormView):
    template_name = 'tests/question.html'
    form_class = TestTakeForm

    def dispatch(self, request, *args, **kwargs):
        self.test = get_object_or_404(Tests, id=self.kwargs['test_id'])

        result, url = TakeTestService.check_session_test(
            test=self.test, 
            session=self.request.session, 
            http_response=self.request
        )

        if result == 'redirect':
            return redirect(url)

        return super().dispatch(request, *args, **kwargs)


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        is_mobile = self.request.user_agent.is_mobile
        question_order = self.request.session['question_order']
        question_index = self.request.session['question_index']
        current_question_id = question_order[question_index]
        self.current_question = get_object_or_404(Question.objects.select_related('group'), id=current_question_id)

        kwargs['is_mobile'] = is_mobile
        kwargs['question'] = self.current_question
        return kwargs


    def form_valid(self, form):
        # print(self.request.POST)
        # print(self.request.user_agent.is_mobile)
        result, url = TakeTestService.form_valid(
            form=form,
            session=self.request.session,
            http_request=self.request,
            current_question=self.current_question
        )

        match result:
            case 'results':
                return redirect(url)
            case 'continue':
                return redirect(url)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_order = self.request.session['question_order']
        question_index = self.request.session['question_index']

        if self.current_question.answer_type == Question.MULTIPLE_CHOICE:
            answers_count = len(self.current_question.answers.filter(is_correct=True).values_list('id', flat=True))
        else:
            answers_count = None 

        context.update({
            'test':self.test,
            'question': self.current_question,
            'answers_count': answers_count,
            'all_questions': {
                'current': question_index + 1,
                'all': len(question_order)
            },
            'test_btn': {
                'text_btn': 'Завершити' if question_index + 1 == len(question_order) else 'Далі'
            },
            'current_question_group': self.current_question.group,
            'remaining_time': self.request.session['remaining_time'],
            'is_mobile': self.request.user_agent.is_mobile
        })
        return context



class TestsResultsView(View):
    template_name = 'tests/test_results.html'

    def get(self, request, test_id):
        result, data = TestResultsService.get(
            session=request.session,
            http_request=request,
            test_id=test_id
        )

        match (result, data):
            case ('redirect', _):
                return redirect(data)
            case ('render', None):
                return render(request, 'tests/success_page_manual_test.html')
            case ('render', dict() as context):
                return render(request, self.template_name, context)
            case _:
                raise ValueError



def success_manual_test(request):
    return render(request, 'tests/success_page_manual_test.html')



class TestsForReviewView(CheckPersonalMixin, CacheMixin ,TemplateView):
    template_name = 'tests/test_for_reviews.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_superuser or not user.is_staff:
            return redirect(reverse("app:index"))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        groups = user.group.prefetch_related(
            Prefetch(
                'test_reviews',
                queryset=TestsReviews.objects.select_related('test').order_by('test', 'test__date_taken').distinct('test'),
                to_attr='reviews_select'
            )
        )

        group_data = {
            f"Group {i}": {
                "group_name": group.name,
                "test_result": [rew.test for rew in group.reviews_select],
            }
            for i, group in enumerate(groups)
        }

        pprint(group_data)


        context.update({'groups': group_data})

        return context



class TestGroupReviewsView(CheckPersonalMixin, TemplateView):
    template_name = 'tests/test_group_reviews.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        test_id = self.kwargs.get('test_id')
        test = get_object_or_404(Tests.objects.select_related('group'), id=test_id)

        user_reviews = TestsReviews.objects.filter(test=test, group=test.group).select_related('user')

        # group_memberships = self.get_user_group(user=user)

        # groups = user.groups.prefetch_related(
        #     Prefetch(
        #         'test_reviews',
        #         queryset=TestsReviews.objects.filter(test=test).select_related('test', 'user'),
        #         to_attr="test_reviews_data"
        #     )
        # )

        context.update({
            'test': test,
            'user_reviews': user_reviews
        })

        return context



class TakeTestReviewView(FormView):
    template_name = 'tests/take_test_review.html'
    form_class = TestReviewForm

    def dispatch(self, request, *args, **kwargs):
        self.test = get_object_or_404(Tests, id=self.kwargs['test_id'])
        self.user = get_object_or_404(User, id=self.kwargs['user_id'])

        self.test_student_responses = TestsReviews.objects.filter(user=self.user, test=self.test).first()

        TakeTestReviewService.dispatch(
            session=self.request.session,
            test=self.test,
            test_student_responses=self.test_student_responses
        )

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        result = TakeTestReviewService.get_form_kwargs(
            session=self.request.session,
            test_student_responses=self.test_student_responses,
        )

        match result:
            case dict():
                self.current_question = result['question']

                kwargs['audio_answers'] = result['audio_answer']
                kwargs['question'] = result['question']
                kwargs['student_question'] = result['student_question']
            case 'Not_found':
                raise Http404('Not question found')

        return kwargs

    def form_valid(self, form):
        if self.request.method == 'POST':
            # question = self.request.session.get('')
            action = self.request.POST.get('action')

        result, data = TakeTestReviewService.form_valid(
            action=action,
            session=self.request.session,
            current_question=self.current_question,
            http_request= self.request,
            form=form,
        )

        match result:
            case 'redirect':
                return redirect(data)

        
        return redirect('tests:take_test_review', test_id=self.kwargs['test_id'],  user_id=self.kwargs['user_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_answers = TakeTestReviewService.get_current_answers(
            current_question=self.current_question,
            # is_mobile=True,
            is_mobile=self.request.user_agent.is_mobile,
        )

        test_review_session = self.request.session['test_review_session']
        question_index = self.request.session['question_index']

        context.update({
            'test': self.test,
            'user': self.user,
            'question': self.current_question,
            'all_questions': {
                "current": question_index + 1,
                "all": len(test_review_session)
            },
            'current_question_group': self.current_question.group,
            'current_answers': current_answers,
            # 'is_mobile': True,
            'is_mobile': self.request.user_agent.is_mobile,
        })
        return context

    
    
class TestReviewResults(View):
    template_name = 'tests/test_review_results.html'

    def get(self, request, *args, **kwargs):
        correct_answers = self.request.session['teacher_answers']
        print(correct_answers)
        test_review_id = self.request.session['test_student_responses_id']
        if test_review_id:
            test_review = TestsReviews.objects.filter(id=test_review_id).select_related('user', 'test', 'group').first()
        else:
            test_review = None

        if test_review:
            user = test_review.user
            test = test_review.test
            duration = test_review.duration
            total_scores = test.questions.aggregate(Sum('scores'))['scores__sum']

        
            score = round((correct_answers / float(total_scores)) * 100) if total_scores > 0 else 0
            # print(score)
            test_result = TestResult.objects.create(
                user=user,
                test=test,
                group=test.group,
                duration=duration,
                score=score,
                attempts=2
            )
            # test_review.delete()
            # print(test_result)

        test_review.delete()
        self.clear_test_session(request)

        return redirect('tests:tests_for_review')
    
    def clear_test_session(self, request):
        """Очищаем данные теста из сессии"""
        session_keys = ['test_student_responses_id','teacher_answers','question_index','test_review_session', 'teacher_responses']
        for key in session_keys:
            if key in session_keys:
                del request.session[key]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
