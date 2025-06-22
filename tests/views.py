# tests/views.py
# Базовые библиотеки
from copyreg import constructor
from decimal import Decimal
from multiprocessing import Value
import os
import random
import base64
from datetime import datetime, timedelta
from wsgiref.util import request_uri

# Импортируем библиотеки Django
from django.utils import timezone
from django.views.generic import FormView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.db.models import F, ExpressionWrapper, Prefetch, Sum, fields
from django.forms import ClearableFileInput, DateInput, DateTimeInput, NumberInput, TextInput, Textarea
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import localtime, now
from django.urls import reverse, reverse_lazy
from django.core.files.base import ContentFile
from django.views import View

# Библиотеки проекта
from common.mixins import CacheMixin
from tests.utils import check_min_datetime, send_emails_from_users
from users.models import User, UsersGroupMembership
from .models import Categories, MatchingPair, QuestionGroup, TestResult, Tests, Question, Answer, TestsReviews
from .forms import MatchingPairForm, QuestionGroupForm, QuestionStudentsForm, TestForm, QuestionForm, AnswerForm, TestReviewForm, TestTakeForm


def index(request):
    return render(request, 'tests/index.html')


class UserRatingView(LoginRequiredMixin, TemplateView):
    template_name = 'tests/rating.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Проверка на принадлежность к группе и статус учителя
        membership = UsersGroupMembership.objects.select_related('group').filter(user=user).first()
        if membership and membership.owner:
            # Пользователь - учитель группы, выводим тесты, которые он выгружал
            context['tests'] = Tests.objects.filter(user=user)  # Все тесты, созданные учителем
        else:
            # Пользователь - студент, выводим его результаты
            test_lists = TestResult.objects.filter(user=user).values_list("test_id", flat=True)
            context['tests'] = Tests.objects.filter(id__in=test_lists)  # Тесты, по которым есть результаты у студента
            

        context.update({
            'group': membership.group if membership and membership.group else None,
            'active_tab': 'rating',
        })

        return context
    

# def rating(request):
#     user = get_object_or_404(User, id=request.user.id)
#     tests = Tests.objects.all()

#     context = {
#         'tests': tests,
#         'user': user,
#         'active_tab': 'rating'
#     }

#     return render(request, 'tests/rating.html', context)


class RatingTestView(LoginRequiredMixin, TemplateView):
    template_name = "tests/rating_test.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, id=self.request.user.id)
        test_id = self.kwargs.get('test_id')


        # Получаем тест и группу пользователя
        test = get_object_or_404(Tests, id=test_id)
        user_group = UsersGroupMembership.objects.filter(user=user).select_related('group').first()

        # Если группа существует возвращаем результаты по тестам всех группы, иначе пустой список
        if user_group:
            group_members = UsersGroupMembership.objects.filter(group=user_group.group).select_related('user')
            results = TestResult.objects.filter(
                 user__id__in=[member.user.id for member in group_members],
                test=test
            ).annotate(
                scores=F('score'),
                duration_seconds=ExpressionWrapper(F('duration'), output_field=fields.DurationField())
            ).order_by('-scores', 'duration_seconds')
        else:
            results = []


        context.update({
            'test': test,
            'results': results,
            'active_tab': 'rating',
        })

        return context

# def rating_test(request, test_id):
#     test = Tests.objects.filter(id=test_id).first()

#     user = get_object_or_404(User, id=request.user.id)

#     user_group = UsersGroupMembership.objects.filter(user=user).first()

#     if user_group:
#         # Получаем всех пользователей, принадлежащих к той же группе, что и текущий пользователь
#         group_members = UsersGroupMembership.objects.filter(group=user_group.group).order_by('user__username')
#     else:
#         group_members = []

#     # Список результатов для каждого члена группы
#     results = [
#         TestResult.objects.filter(user=item.user, test=test).first()
#         for item in group_members
#         if TestResult.objects.filter(user=item.user, test=test).exists()
#     ]

#     # Сортировка результатов по score
#     results = sorted(results, key=lambda x: x.score, reverse=True)

#     context = {
#         'test': test,
#         'user': user,
#         'results': results,
#         'active_tab': 'rating'
#     }

#     return render(request, 'tests/rating_test.html', context=context)


class AllTestsView(LoginRequiredMixin, TemplateView):
    template_name = "tests/all_tests.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Если админ то отображаем все тесты, иначе только тесты текущего пользователя
        if self.request.user.is_superuser:
            tests = Tests.objects.all()
        else:
            tests = Tests.objects.filter(user=self.request.user)

        context.update({
            'tests': tests,
            'active_tab': 'my_tests'
        })

        return context


# def all_tests(request):
#     # messages.success(request, 'Тест!')
#     if request.user.is_superuser:
#         tests = Tests.objects.all()
#     else:
#         tests = Tests.objects.filter(user=request.user)


#     return render(request, 'tests/all_tests.html', {'tests': tests, "active_tab": "my_tests"})


class CreateTestView(LoginRequiredMixin, FormView):
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

        return self.render_to_response({'form': form, 'errors': errors})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Доабвление active_tab необходимо для правильной работы стилей ссылок в header 
        context['active_tab'] = 'create'
        return context
    
    def get_success_url(self) -> str:
        return reverse('tests:add_questions', kwargs={'test_id': self.object.id})
    

class EditTestView(UpdateView):
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


# @login_required
# def create_test(request):
#     if request.method == 'POST':
#         form = TestForm(request.POST, request.FILES, user=request.user)
#         if form.is_valid():
#             # Сначала создаем тест, но не сохраняем его в базе
#             test = form.save(commit=False)  
#             test.user = request.user  # Присваиваем пользователя

#             # Получаем список ID студентов
#             selected_students = form.cleaned_data.get('students')
            
#             # Сохраняем студентов в поле JSON в формате [1, 2, 3]
#             test.students = {'students': selected_students}
            
#             # Сохраняем тест
#             test.save()

#             # Далее можно перенаправить на другую страницу
#             return redirect('tests:add_questions', test_id=test.id)
#     else:
#         form = TestForm(user=request.user)
    
#     return render(request, 'tests/create_test.html', {'form': form})


def delete_test(request, test_id):
    test = get_object_or_404(Tests, id=test_id)
    test.delete()
    return redirect('app:index')


class AddQuestionGroupView(LoginRequiredMixin, FormView):
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
    

# @login_required
# def add_question_group(request, test_id):
#     test = get_object_or_404(Tests, pk=test_id)

#     if request.method == 'POST':
#         form = QuestionGroupForm(request.POST)
#         if form.is_valid():
#             question_group = form.save(commit=False)
#             question_group.test = test
#             question_group.save()
#             return redirect("tests:add_questions",  test_id=test.id)

#     else:
#         form = QuestionGroupForm()


#     context = dict(form=form)

#     return render(request, 'tests/adq.html', context=context)
    

class AddQuestionsView(LoginRequiredMixin, TemplateView):
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
                test.students = {'students': students_form.cleaned_data.get('students')}
                test.save()
                send_emails_from_users(data_users, test)
                return JsonResponse({'status': 'success', 'message': 'Студенты обновлены.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Opps, помилка'})
            
        
        context = self.get_context_data()
        context['question_form'] = question_form
        context['form_students'] = students_form
        return self.render_to_response(context)


# @login_required
# def add_questions(request, test_id):
#     user = get_object_or_404(User, id=request.user.id)
#     test = get_object_or_404(Tests, pk=test_id)
#     question_groups = QuestionGroup.objects.filter(test=test).prefetch_related('questions_group')
#     ungrouped_questions = Question.objects.filter(test=test, group__isnull=True)

#     # POST-запрос: Обрабатываем форму в зависимости от переданного form_type
#     if request.method == 'POST':
#         form_type = request.POST.get('form_type')  # Определяем тип формы

#         # Обработка формы вопросов
#         question_form = QuestionForm(request.POST, request.FILES, test=test)

#         # Обработка формы студентов
#         student_form = QuestionStudentsForm(request.POST, request.FILES, test=test, user=user)

#         if form_type == 'form_question':
#             if question_form.is_valid():
#                 question = question_form.save(commit=False)
#                 question.test = test  # Привязываем вопрос к текущему тесту
#                 question.save()
#                 return redirect('tests:add_questions', test_id=test.id)

#         elif form_type == 'form_student':
#             if student_form.is_valid():
#                 test.students = {'students': student_form.cleaned_data.get('students')}
#                 test.save()
#                 return redirect('tests:add_questions', test_id=test.id)
#             else:
#                 print(student_form.errors)
#                 return redirect('tests:add_questions', test_id=test.id)

#     else:
#         question_form = QuestionForm(test=test)
#         student_form = QuestionStudentsForm(test=test, user=user)    

#     # Запросы для отображения данных
#     questions = Question.objects.filter(test=test)

#     # Контекст для шаблона
#     context = {
#         'test': test,
#         'question_form': question_form,  
#         'questions': questions,  # Список всех вопросов
#         'question_groups': question_groups,  # Группированные вопросы
#         'ungrouped_questions': ungrouped_questions,  # Негруппированные вопросы
#         'form_student': student_form  # Форма для выбора студентов
        
#     }

#     return render(request, 'tests/add_questions.html', context=context)


def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    test = get_object_or_404(Tests, id=question.test.id)
    question.delete()
    return redirect('tests:add_questions', test_id=test.id)


def complete_questions(request, test_id):
    return redirect('app:index')


class AddAnswersView(LoginRequiredMixin, FormView):
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


# @login_required
# def add_answers(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     test = question.test
#     questions = test.questions.all()


#     if request.method == 'POST':
#         answer_form = AnswerForm(request.POST)
#         if answer_form.is_valid():
#             answer = answer_form.save(commit=False)
#             answer.question = question
#             answer.save()
#             return redirect('tests:add_answers', question_id=question.id)
#     else:
#         answer_form = AnswerForm()
#     return render(request, 'tests/add_answer.html', {
#         'test': test,
#         'question': question,
#         'questions': questions,
#         'form': answer_form,
#         'form_type':'Ответ',
#         'action_url':'tests:add_answers',
#     })


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


def delete_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    question = get_object_or_404(Question, id=answer.question.id)
    answer.delete()
    question.update_question_score()
    return redirect('tests:add_answers', question_id=question.id)


class AddMathicngPairView(LoginRequiredMixin, FormView):
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


def delete_matching_pair(request, pair_id):
    matching_pair = get_object_or_404(MatchingPair, id=pair_id)
    question = get_object_or_404(Question, id=matching_pair.question.id)
    matching_pair.delete()
    question.update_question_score()
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

#     test = question.test
#     questions = test.questions.all()
        

# def add_matching_pair(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     test = question.test
#     questions = test.questions.all()


#     if request.method == "POST":
#         matching_pair_form = MatchingPairForm(request.POST)
#         if matching_pair_form.is_valid():
#             answer = matching_pair_form.save(commit=False)
#             answer.question = question
#             answer.save()
#             return redirect('tests:add_matching_pair', question_id=question.id)
#     else:
#         matching_pair_form = MatchingPairForm()
#     return render(request, 'tests/add_answer.html', {
#         'test': test,
#         'question': question,
#         'questions': questions,
#         'form': matching_pair_form,
#         "form_type":"Соотвецтвие",
#         "action_url":'tests:add_matching_pair',
#     })


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
    

# def test_preview(request, test_id):
#     if request.user.is_authenticated:
#         test_results = request.user.test_results.all()
#         test = get_object_or_404(Tests, id=test_id)
#         user_test = TestResult.objects.filter(user=request.user, test=test)
#         if len(user_test) > 0:
#             if user_test[0].remaining_atemps > 0:
#                 test_required = True
#             else:
#                 test_required = False
#         else:
#             test_required = True

#     else:
#         test_results = ['Для того чтобы пройти тест зарегестрируйтесь :D']

#     test = get_object_or_404(Tests, pk=test_id)

#     context = {
#         "test": test,
#         'test_results': test_results,
#         'required_attemps': test_required,
#     }

#     return render(request, 'tests/test_preview.html', context=context)


class TakeTestView(LoginRequiredMixin ,FormView):
    template_name = 'tests/question.html'
    form_class = TestTakeForm

    def dispatch(self, request, *args, **kwargs):
        self.test = get_object_or_404(Tests, id=self.kwargs['test_id'])
        server_time = timezone.make_aware(datetime.now(), timezone.get_default_timezone())

        if server_time < localtime(self.test.date_in) or server_time > localtime(self.test.date_out):
            if 'test_responses' in request.session:

                if len(request.session.get('test_responses')) != 0:
                    return redirect('tests:test_results', test_id=self.kwargs['test_id'])
                else:
                    print('return 2')
                    self.clear_test_session(request=request)
                    return redirect('app:index')
                
            else:
                print('return 1')
                return redirect('app:index')

        # При неверном ID теста в сессии очищаем сессию
        session_test_id = request.session.get('test_id')
        if self.test.id != session_test_id and session_test_id != None:
            self.clear_test_session(request=request)

        # Снова добавляем ID теста к сессии
        request.session['test_id'] = self.test.id

        # Если время начала теста не установленио то добавляем его в сессию
        if 'test_start_time' not in request.session:
            request.session['test_start_time'] = now().timestamp()  # Сохраняем метку времени

        # Если не установлено оставшееся время(от теста) то добавляем его в сессию
        if 'remaining_time' not in request.session:
            request.session['remaining_time'] = self.test.duration.total_seconds()

        # Если сессия для теста не была созданна тогда иничиализируем сессию теста
        if 'question_order' not in request.session:
            response = self.initialize_test_session()
            if isinstance(response, HttpResponse):
                return response

        return super().dispatch(request, *args, **kwargs)

    def clear_test_session(self, request):
        # Очищаем все возможные ключи из сессии
        keys_to_clear = ['test_id', 'question_order', 'question_index', 'test_responses', 'remaining_time', 'test_start_time']
        for key in keys_to_clear:
            if key in request.session:
                del request.session[key]

    def initialize_test_session(self):
        questions_by_group = {}

        # Проходим по группе вопросов и все вопросы для каждой из них после сохраняем в виде словаря Группа:[Вопросы]
        for group in QuestionGroup.objects.filter(test=self.test).prefetch_related('questions_group'):
            questions_by_group[group.name] = list(group.questions_group.all())

        # Проходим по словарю questions_by_group и перемещиваем все вопросы для каждой группы
        for group_name, questions in questions_by_group.items():
            random.shuffle(questions)

        # Обединяем все перемешанные вопросы в один список
        all_questions = []
        for questions in questions_by_group.values():
            all_questions.extend(questions)

        # Выбираем оставшиеся вопросы которые не предналежат ни одной из групп после чего перемешиваем их и добавляем в список
        questions_not_group = list(Question.objects.filter(test=self.test, group=None))
        random.shuffle(questions_not_group)
        all_questions.extend(questions_not_group)

        if len(all_questions) == 0:
            # Если нет вопросов, то очищаем сессию и перенаправляем на главную страницу
            self.clear_test_session(request=self.request)
            return redirect('app:index')
        else:
            # Иначе инициализируем начальные данные для прохождения теста
            self.request.session['question_order'] = [q.id for q in all_questions]
            self.request.session['question_index'] = 0  # Начинаем с первого вопроса
            self.request.session['test_responses'] = {}  # Для хранения ответов

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        question_order = self.request.session['question_order']
        question_index = self.request.session['question_index']
        current_question_id = question_order[question_index]
        self.current_question = get_object_or_404(Question.objects.select_related('group'), id=current_question_id)

        kwargs['question'] = self.current_question
        return kwargs

    def form_valid(self, form):
        answer = form.cleaned_data.get('answer')

        if self.current_question.question_type == 'AUD' or self.current_question.question_type == 'IMG' or self.current_question.question_type == 'TXT':
            if self.current_question.answer_type == 'AUD':
                audio_answer = form.cleaned_data.get(f'audio_answer_{self.current_question.id}', None)
                if audio_answer is not None:
                    self.request.session['test_responses'][f"audio_answer_{self.current_question.id}"] = audio_answer
            else:
                if answer:
                    self.request.session['test_responses'][f"question_{self.current_question.id}"] = answer

        elif self.current_question.question_type == 'MTCH':
            responses = self.request.POST
            dict_items = {}
            for left, right in responses.items():
                if left.startswith('answer_'):
                    left_item = left.split('answer_')[1]
                    dict_items[left_item] = right
            self.request.session['test_responses'][f"question_{self.current_question.id}_type_matching"] = dict_items
        else:
            if answer:
                self.request.session['test_responses'][f"question_{self.current_question.id}"] = answer

        remaining_time = int(self.request.POST.get('remaining_time', 0))
        self.request.session['remaining_time'] = remaining_time

        self.request.session['question_index'] += 1

        question_order = self.request.session['question_order']
        question_index = self.request.session['question_index']
        if question_index >= len(question_order):
            return redirect('tests:test_results', test_id=self.kwargs['test_id'])

        return redirect('tests:take_test', test_id=self.kwargs['test_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_order = self.request.session['question_order']
        question_index = self.request.session['question_index']

        context.update({
            'test':self.test,
            'question': self.current_question,
            'all_questions': {
                'current': question_index + 1,
                'all': len(question_order)
            },
            'test_btn': {
                'text_btn': 'Завершити' if question_index + 1 == len(question_order) else 'Далі'
            },
            'current_question_group': self.current_question.group,
            'remaining_time': self.request.session['remaining_time']
        })
        return context


# def take_test(request, test_id):
#     test = get_object_or_404(Tests, id=test_id)
#     request.session['test_id'] = test.id

#      # Сохраняем время начала теста, если оно ещё не сохранено
#     if 'test_start_time' not in request.session:
#         request.session['test_start_time'] = now().timestamp()  # Сохраняем текущую метку времени

#     # Если тест ещё не завершён
#     if 'remaining_time' not in request.session:
#         request.session['remaining_time'] = test.duration.total_seconds()  # Начальное значение таймера
    
#     # Если тест только начался, инициализируем сессию для теста
#     if 'question_order' not in request.session:
#         # Получаем вопросы, отсортированные по группам
#         questions_by_group = {}
#         for group in QuestionGroup.objects.filter(test=test):
#             questions_by_group[group.name] = list(group.questions_group.all())

#         # Перемешиваем вопросы внутри каждой группы
#         for group_name, questions in questions_by_group.items():
#             random.shuffle(questions)  # Перемешиваем вопросы в группе

#         # Объединяем все перемешанные вопросы в один список
#         all_questions = []
#         for group_name, questions in questions_by_group.items():
#             all_questions.extend(questions)

#         #Для вопросов без группы
#         questions_not_group = {}
#         # for group in Question.objects.filter(test=test, group=None):
#         questions_not_group['All'] = list(Question.objects.filter(test=test, group=None))

#         # Перемешиваем вопросы и добавляем их к остальным
#         for _ , questions in questions_not_group.items():
#             random.shuffle(questions)
#             all_questions.extend(questions)


    
#         # Сохраняем порядок вопросов в сессии
#         request.session['question_order'] = [q.id for q in all_questions]
#         request.session['question_index'] = 0  # Начинаем с первого вопроса
#         request.session['test_responses'] = {}  # Для хранения ответов пользователя


#     question_order = request.session['question_order']
#     question_index = request.session['question_index']
    
#     # Проверяем, не завершен ли тест (когда все вопросы пройдены)
#     if question_index >= len(question_order):
#             return redirect('tests:test_results', test_id=test_id)
    
#     # Текущий вопрос
#     current_question_id = question_order[question_index]
#     current_question = get_object_or_404(Question, id=current_question_id)
#     # current_question_group = QuestionGroup.objects.filter(question=current_question).first()

#     try:
#         current_question_group = current_question.group.name
#     except:
#         current_question_group = 'Усі'
    
#     # Форма для текущего вопроса
#     if request.method == 'POST':
#         form = TestTakeForm(request.POST, question=current_question)
#         if form.is_valid():
#             # Обрабатываем разные типы вопросов
#             if current_question.question_type == 'AUD':
#                 # Для аудиовопросов используем 'audio_answer'
#                 answer = form.cleaned_data.get(f'audio_answer_{current_question_id}', None)
#             else:
#                 # Для всех остальных вопросов используем 'answer'
#                 answer = form.cleaned_data.get('answer', None)

#             if current_question.question_type == 'AUD':
#                 # Сохраняем в сессии с префиксом 'audio_answer_'
#                 if answer is not None:
#                     request.session['test_responses'][f"audio_answer_{current_question_id}"] = answer
#             elif current_question.question_type == 'MTCH':
#                 responses = request.POST


#                 dict_items = {}
#                 for left, right in responses.items():
#                    if left.startswith('answer_'):  # Проверяем, что это поле с ответом
#                         left_item = left.split('answer_')[1]  # Получаем левый элемент
#                         dict_items[left_item] = right
                
#                 request.session['test_responses'][f'question_{current_question_id}_type_matching'] = dict_items


#             else:
#                 # Для всех остальных типов вопросов используем 'question_{id}'
#                 if answer is not None:
#                     request.session['test_responses'][f"question_{current_question_id}"] = answer

#             remaining_time = int(request.POST.get('remaining_time', 0))
#             request.session['remaining_time'] = remaining_time  # Обновляем оставшееся время
                            
#             # Переход к следующему вопросу
#             request.session['question_index'] += 1

#             return redirect('tests:take_test', test_id=test_id)  # Перезагрузка на следующий вопрос
#     else:
#         form = TestTakeForm(question=current_question)

#     # Статистика по вопросам
#     all_questions = {
#         "current": question_index + 1,
#         "all": len(question_order)
#     }

#     return render(request, 'tests/question.html', {
#         'form': form,
#         'test': test,
#         'question': current_question,
#         'all_questions': all_questions,
#         'current_question_group': current_question_group,
#         'remaining_time': request.session['remaining_time'],
#     })


class TestsResultsView(View):
    template_name = 'tests/test_results.html'

    def get(self, request, test_id):
        test = get_object_or_404(Tests, id=test_id)
        responses = request.session.get('test_responses', {})
        audio_answers = request.session.get('autio_answer_', {})
        test_time = request.session.get('remaining_time', None)

        if test.check_type == Tests.MANUAL_CHECK:
            self.save_audio_responses(request, responses, audio_answers)
            self.clear_test_session(request)

            if not test_time or not responses:
                return redirect('app:index')
            
            test_duration = timedelta(seconds=test.duration.total_seconds() - test_time)
            TestsReviews.objects.create(
                test=test,
                user=request.user,
                answers=responses,
                audio_answers=audio_answers,
                duration=test_duration,
            )
            return render(request, 'tests/success_page_manual_test.html')
        else:

            if not test_time:
                return redirect('app:index')
            
            score, correct_answers, total_questions, test_duration = self.calculate_results(test, responses, test_time)
            self.save_test_results(request, test, score, test_duration)
            self.clear_test_session(request)
            context = self.get_context_data(test, score, correct_answers, total_questions)
            return render(request, self.template_name, context)
    
    def save_audio_responses(self, request, responses, audio_answers):
        for key, value in responses.items():
            if 'audio_answer_' in key and value:
                question_id = key.split('audio_answer_')[1]
                audio_data = value.split(',')[1]
                audio_content = base64.b64decode(audio_data)


                filename = f'audio_answer_{question_id}_{request.user.id}.wav'
                file_path = os.path.join('answers/audios/', filename)
                audio_file = ContentFile(audio_content, filename)
                saved_file = default_storage.save(file_path, audio_file) 
                file_url = default_storage.url(saved_file)
                audio_answers[question_id] = file_url

                responses[f'audio_answer_{question_id}'] = 'Перенесён'

        request.session['audio_answers'] = audio_answers   


    
    def calculate_results(self, test, responses, test_time):
        total_questions = test.questions.count()
        total_points = test.questions.aggregate(Sum('scores'))['scores__sum']
        print('TOTAL POINTS', total_points)
        correct_answers = 0.0
        complete_answers = 0


        for key, value in responses.items():
            if key.startswith('question_'):
                question_id = int(key.split('_')[1])
                question = Question.objects.get(id=question_id)
                complete, correct_answer = self.evaluate_question(question, value)
                correct_answers += correct_answer 
                print("ОЧКИ ВОПРОСА", question.scores)
                print("ОЧКИ ответа", int(correct_answers))
                if complete:
                    complete_answers += 1

        
        score = round((correct_answers / total_points) * 100) if total_questions > 0 else 0
        test_duration = timedelta(seconds=test.duration.total_seconds() - test_time)

        return score, int(complete_answers), total_questions, test_duration

    def evaluate_question(self, question, value):
        correct_answers = 0.0
        complete_question = False

        if question.question_type == 'MTCH':

            if question.scores_for == Question.SCORE_FOR_ANSWER:
            # questions_count = MatchingPair.objects.filter(question=question).count()

                for left, right in value.items():
                    match = MatchingPair.objects.filter(question=question, left_item=left, right_item=right).first()
                    if match:
                        correct_answers += match.score

                    if correct_answers == question.scores:
                            complete_question = True

            elif question.scores_for == Question.SCORE_FOR_QUESTION:
                matching_pair_dict = {
                    str(left_item): right_item
                    for left_item, right_item in question.matching_pairs.all().values_list('left_item', 'right_item')
                }

                if len(matching_pair_dict) > 0:
                    point = question.scores / len(matching_pair_dict)
                else:
                    # Возвращаем 0 в очках так как правильных ответов 0
                    return complete_question, correct_answers

                for left, right in value.items():
                    if str(left) in matching_pair_dict:
                        
                        expected_right = matching_pair_dict[left]
                        if right == expected_right:
                            correct_answers += point

                if question.scores == correct_answers:
                    complete_question = True

        elif question.answer_type == 'SC':

            if question.scores_for == Question.SCORE_FOR_ANSWER:
                correct_answer = question.answers.filter(is_correct=True).first()
                
                try:
                    if correct_answer and correct_answer.id == int(value):
                        correct_answers += correct_answer.score
                        if correct_answers == question.scores:
                            complete_question = True
                except ValueError as e:
                    print(e)
                
            elif question.scores_for == Question.SCORE_FOR_QUESTION:
                correct_answer = question.answers.filter(is_correct=True).first()

                try:
                    if correct_answer and correct_answer.id == int(value):
                        correct_answers += question.scores
                        complete_question = True
                except ValueError as e:
                    print(e)

                                

        elif question.answer_type == 'MC':
                
                if question.scores_for == Question.SCORE_FOR_ANSWER:
                    correct_answers_dict = {
                        str(answer_id): score    
                        for answer_id, score in question.answers.filter(is_correct=True).values_list('id', 'score')
                    }

                    for v in value:
                        if str(v) in correct_answers_dict:
                            correct_answers += correct_answers_dict[v]

                    if correct_answers == question.scores:
                        complete_question = True

                elif question.scores_for == Question.SCORE_FOR_QUESTION:
                    correct_answers_list = question.answers.filter(is_correct=True).values_list('id', flat=True)

                    if len(correct_answers_list) > 0:
                        points = question.scores / len(correct_answers_list)
                    else:
                        return complete_question, correct_answers

                    try:
                        for v in value:
                            if int(v) in correct_answers_list:
                                correct_answers += points
                    except ValueError as e:
                        print(e)

                    if correct_answers == question.scores:
                        complete_question = True


        elif question.answer_type == 'INP':
            if question.scores_for == Question.SCORE_FOR_ANSWER:
                correct_answers_dict = {
                    str(text).strip().lower(): score
                    for text, score in question.answers.filter(is_correct=True).values_list('text', 'score')
                }
                    
                if correct_answers_dict:
                    if str(value).strip().lower() in correct_answers_dict:

                        correct_answers += correct_answers_dict[value]

                        if correct_answers == question.scores:
                                complete_question = True

            elif question.scores_for == Question.SCORE_FOR_QUESTION:
                correct_answers_list = [
                    str(v).lower().strip() for v in question.answers.filter(is_correct=True).values_list('text', flat=True)
                ]

                if str(value).lower().strip() in correct_answers_list:
                    correct_answers += question.scores
                    complete_question = True



        print("ОТВЕТ", question, correct_answers,":", complete_question)
        return complete_question ,correct_answers
    
    def save_test_results(self, request, test, score, test_duration):
        test_result, created = TestResult.objects.get_or_create(
            user=request.user,
            test=test,
            defaults={'score': score, 'attempts': 1, 'duration': test_duration}
        )

        if not created:
            if test_result.remaining_atemps > 0:
                test_result.attempts += 1
                test_result.duration = test_duration
                test_result.score = max(test_result.score, score)
                test_result.save()
                
    def clear_test_session(self, request):
        session_keys = ['question_order','question_index','test_responses','remaining_time', 'test_id']
        for key in session_keys:
            if key in request.session:
                del request.session[key]

    def get_context_data(self, test, score, correct_answers, total_questions):
        return {
            'test': test,
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
        }
    

# def test_results(request, test_id):
#     test = get_object_or_404(Tests, id=test_id)
#     responses = request.session.get('test_responses', {})
#     audio_answers = request.session.get('audio_answer_', {})
#     test_time = request.session.get('remaining_time', None)
    

#     if test.check_type == Tests.MANUAL_CHECK:
#             for key, value in responses.items():
#                 if 'audio_answer_' in key and value:
#                     # Преобразуем base64 в файл
#                     question_id = key.split('audio_answer_')[1]
#                     audio_data = value.split(',')[1]  # Убираем префикс base64
#                     audio_content = base64.b64decode(audio_data)
                    
#                     # Генерируем имя файла
#                     filename = f"audio_answer_{question_id}_{request.user.id}.webm"
#                     file_path = os.path.join('answers/audios/', filename)
#                     audio_file = ContentFile(audio_content, filename)
                    
#                     # Сохраняем файл в систему
#                     saved_file = default_storage.save(file_path, audio_file)
                    
#                     # Получаем URL файла
#                     file_url = default_storage.url(saved_file)
                    
#                     # Сохраняем URL аудиофайла по вопросу в словаре
#                     audio_answers[question_id] = file_url

#             request.session['audio_answers'] = audio_answers


#     if test.check_type == Tests.MANUAL_CHECK:
#         print('hellow')
#         review = TestsReviews.objects.create(
#             test=test,
#             user=request.user,
#             answers=responses,
#             audio_answers=audio_answers,  # Сохраняем аудио-ответы для ручной проверки
#                 # group=request.user.profile.group,  # Если у пользователя есть группа
#         )
#         print(review)

#         # print(request.session)
#         if 'question_order' in request.session:
#             del request.session['question_order']
#         if 'question_index' in request.session:
#             del request.session['question_index']
#         if 'test_responses' in request.session:
#             del request.session['test_responses']
#         if 'remaining_time' in request.session:
#             del request.session['remaining_time']

#         return render(request, 'tests/success_page_manual_test.html')
    
#     else:
    

#         total_questions = test.questions.count()
#         correct_answers = 0.0


#         for key, value in responses.items():
#             if key.startswith('question_'):
#                 question_id = int(key.split('_')[1])
#                 question = Question.objects.get(id=question_id)
                
#                 if question.question_type == 'SC':
#                     correct_answer = question.answers.filter(is_correct=True).first()
#                     if correct_answer and correct_answer.id == int(value):
#                         correct_answers += 1.0
#                 elif question.question_type == 'MC':
#                     correct_answers_list = question.answers.filter(is_correct=True).values_list('id', flat=True)
#                     if set(map(int, value)) == set(correct_answers_list):
#                         correct_answers += 1.0
#                 elif question.question_type == 'IMG':
#                     correct_answer = question.answers.filter(is_correct=True).first()
#                     if correct_answer and correct_answer.id == int(value):
#                         correct_answers += 1.0
#                 elif question.question_type == 'AUD':
#                     correct_answer = question.answers.filter(is_correct=True).first()
#                     if correct_answer and correct_answer.id == int(value):
#                         correct_answers += 1.0
#                 elif question.question_type == "INP":
#                     correct_answer = question.answers.filter(is_correct=True).first()
#                     if str(correct_answer).strip().lower() == str(value).strip().lower():
#                         correct_answers += 1.0
#                 elif question.question_type == 'MTCH':
#                     questions_count = MatchingPair.objects.filter(question=question).count()
#                     points = 1 / questions_count
                    
#                     for left, right in value.items():
#                         if MatchingPair.objects.filter(question=question, left_item=left, right_item=right).exists():
#                             correct_answers += points 

#         try:
#             score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
#             score = round(score)
#         except ZeroDivisionError as e:
#             print(e)
#             score = 0


#         test_duration = test.duration.total_seconds() - test_time
#         test_duration = timedelta(seconds=test_duration)


#         if request.user.is_authenticated:
#             test_result, created = TestResult.objects.get_or_create(
#                 user=request.user,
#                 test=test,
#                 defaults={'score': score, 'attempts': 1, 'duration': test_duration}
#             )
            
#             if not created:
#                 if test_result.remaining_atemps > 0:
#                     test_result.attempts += 1
#                     test_result.duration = test_duration
#                     test_result.score = max(test_result.score, score)  # Сохраняем лучший результат
#                     test_result.save()
#                 else:
#                     return render(request, 'users/profile.html')
        
#         if 'question_order' in request.session:
#             del request.session['question_order']
#         if 'question_index' in request.session:
#             del request.session['question_index']
#         if 'test_responses' in request.session:
#             del request.session['test_responses']
#         if 'test_id' in request.session:
#             del request.session['test_id']
#         if 'remaining_time' in request.session:
#             del request.session['remaining_time']

#         correct_answers = int(correct_answers)
            
#     context = {
#         'test': test,
#         'score': score,
#         'correct_answers': correct_answers,
#         'total_questions': total_questions
#     }
    
#     return render(request, 'tests/test_results.html', context)

def success_manual_test(request):
    return render(request, 'tests/success_page_manual_test.html')


class TestsForReviewView(CacheMixin ,TemplateView):
    template_name = 'tests/test_for_reviews.html'

    def dispatch(self, request, *args, **kwargs):
        user= request.user
        if not user.is_superuser or not user.is_staff:
            return redirect(reverse("app:index"))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, id=self.request.user.id)

        user_groups = self.set_get_cache(
            UsersGroupMembership.objects.filter(user=user).select_related('group'),
            f"user_group_{user.id}",
            30,
        )
        # user_groups = UsersGroupMembership.objects.filter(user=user).select_related('group')

        if user_groups.exists():
            # group = user_groups.first().group
            group = self.set_get_cache(user_groups[0].group, f"user_first_group_{user.id}", 30)

            group_memberships = UsersGroupMembership.objects.filter(group=group).select_related('user')

            # tests_reviews = Tests.objects.filter(
            #     user__in=[member.user for member in group_memberships],
            #     check_type="manual"
            # )
            tests_reviews = self.set_get_cache(
                Tests.objects.filter(
                    user__in=[member.user for member in group_memberships],
                    check_type="manual"),
                f"test_reviews_{user.id}",
                30,
            )
        else:
            tests_reviews = Tests.objects.none()

        context.update({
            'test_result': tests_reviews,
            'active_tab': 'my_tests'
        })

        return context


# def tests_for_review(request):
#     user = get_object_or_404(User, id=request.user.id)
#     user_groups = UsersGroupMembership.objects.filter(user=user)

#     # Проверяем в какой группе находиться пользоваетель
#     if user_groups.exists():
#         group = user_groups.first().group
#         group_memberships = UsersGroupMembership.objects.filter(group=group)
    
    
#     tests_reviews = []
#     for item in group_memberships:
#         test = Tests.objects.filter(user=item.user, check_type='manual')
#         if test:
#             tests_reviews.append(test)

#     tests_results = []
#     for t in tests_reviews:
#         for ti in t:
#             if ti:
#                 tests_results.append(ti)

#     context = {
#         "test_result": tests_results,
#     }


#     return render(request, 'tests/tr.html', context=context)


class TestGroupReviewsView(TemplateView):
    template_name = 'tests/test_group_reviews.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        test_id = self.kwargs.get('test_id')
        test = get_object_or_404(Tests, id=test_id)
        user = get_object_or_404(User, id=self.request.user.id)

        group_memberships = self.get_user_group(user=user)

        # user_reviews = []

        user_reviews = (
            TestsReviews.objects.filter(test=test, user__id__in=group_memberships)
            .select_related('user')  # Оптимизируем запросы, подтягивая данные пользователей
        )

        context.update({
            'test': test,
            'user_reviews': user_reviews
        })

        return context

    def get_user_group(self, user):
        user_membership = UsersGroupMembership.objects.filter(user=user).select_related('group').first()

        if user_membership and user_membership.group:
            return (
                UsersGroupMembership.objects.filter(group=user_membership.group)
                .values_list('user_id', flat=True)
            )
        else:
            return []


# def test_group_reviews(request, test_id):
#     test = get_object_or_404(Tests, id=test_id)
#     user = get_object_or_404(User, id=request.user.id)

#     user_groups = UsersGroupMembership.objects.filter(user=user)

#     if user_groups.exists():
#         group = user_groups.first().group
#         group_memberships = UsersGroupMembership.objects.filter(group=group)
#         group_name = group.name
#     else:
#         group = None
#         group_memberships = None
#         group_name = "Вы не присоединились к группе"

#     user_complitely_test = []
#     user_reviews = []
#     user_not_reviews = []
#     for us in group_memberships:
#         review = TestsReviews.objects.filter(user=us.user, test=test)
#         results = TestResult.objects.filter(user=us.user, test=test)
#         if review:    
#             user_reviews.append(review)
#         elif results:
#             user_complitely_test.append(results)
#         else:
#             user_not_reviews.append(us.user)


#     context = {
#         'user_reviews': user_reviews,
#         'user_not_reviews': user_not_reviews,
#         'user_complete_test': user_complitely_test,
#     }


#     return render(request, 'tests/test_group_reviews.html', context=context)
    

class TakeTestReviewView(FormView):
    template_name = 'tests/take_test_review.html'
    form_class = TestReviewForm

    def dispatch(self, request, *args, **kwargs):
        self.test = get_object_or_404(Tests, id=self.kwargs['test_id'])
        self.user = get_object_or_404(User, id=self.kwargs['user_id'])

        self.test_student_responses = TestsReviews.objects.filter(user=self.user, test=self.test).first()

        if 'teacher_answers' not in request.session:
            request.session['teacher_answers'] = 0.0
        
        required_keys = ['teacher_answers', 'test_review_session', 'question_index', 'teacher_responses', 'test_student_responses_id']
        
        missing_keys = [key for key in required_keys if key not in request.session]
        
        if missing_keys:
            self.initialize_session_test()

        return super().dispatch(request, *args, **kwargs)

    def initialize_session_test(self):
        questions = Question.objects.filter(test=self.test)

        if len(questions) == 0:
            self.request.session['test_review_session'] = []
        else:
            self.request.session['test_review_session'] = [q.id for q in questions]

        self.request.session['question_index'] = 0
        self.request.session['teacher_responses'] = {}
        # self.request.session['correct_answers'] = 0.0
        self.request.session['test_student_responses_id'] = self.test_student_responses.id
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        question_order = self.request.session['test_review_session']
        question = self.request.session['question_index']
        
        current_question_id = question_order[question]
        self.current_question = get_object_or_404(Question.objects.select_related('group').prefetch_related('matching_pairs','answers'), id=current_question_id)

    # Проверка на существование и инициализация атрибутов, если они равны None
        # if not hasattr(self.test_student_responses, 'answers') or self.test_student_responses.answers is None:
        #     self.test_student_responses.answers = {}
        # if not hasattr(self.test_student_responses, 'audio_answers') or self.test_student_responses.audio_answers is None:
        #     self.test_student_responses.audio_answers = {}

        if self.current_question.answer_type == 'AUD':
            self.current_students_question = self.test_student_responses.audio_answers.get(f'audio_answer_{current_question_id}', [])
        elif self.current_question.question_type == 'MTCH':
            self.current_students_question = self.test_student_responses.answers.get(f'question_{current_question_id}_type_matching', [])
        else:
            self.current_students_question = self.test_student_responses.answers.get(f'question_{current_question_id}', [])

        kwargs['audio_answers'] = self.test_student_responses.audio_answers
        kwargs['question'] = self.current_question
        kwargs['student_question'] = self.current_students_question
        return kwargs

    def form_valid(self, form):
        if self.request.method == 'POST':
            question = self.request.session.get('')
            action = self.request.POST.get('action')

            if action == 'correct':
                self.request.session['teacher_answers'] += float(self.current_question.scores)

            elif action == 'incorrect':
                ...

            elif action == 'partial':
                print(self.request.POST)

                if self.current_question.question_type == 'MTCH':
                    if self.current_question.scores_for == Question.SCORE_FOR_ANSWER:
                        matching_pairs_dict = {
                            str(pair.left_item): pair.score
                            for pair in self.current_question.matching_pairs.all()
                        }

                        print(matching_pairs_dict)
                        matching_pairs =  {
                            left: right
                            for left, right in self.current_question.matching_pairs.all().values_list('left_item', 'right_item')
                        }

                        print(matching_pairs)

                        for key, value in self.request.POST.items():
                            if key.startswith('answer_'):
                                # Получаем наш левый и правый ответ
                                left_item = key.replace('answer_', '')
                                right_item = value

                                # Проверяем наличие в словаре ответов
                                if left_item in matching_pairs:
                                    
                                    # Если елемент найден то также проверяем что right совпадает если так то засчитываем балл
                                    expect_right = matching_pairs[left_item]
                                    if right_item == expect_right:
                                        self.request.session['teacher_answers'] += matching_pairs_dict[left_item]

                    elif self.current_question.scores_for == Question.SCORE_FOR_QUESTION:
                        matching_pairs_dict =  {
                            str(left): right
                            for left, right in self.current_question.matching_pairs.all().values_list('left_item', 'right_item')
                        }

                        if len(matching_pairs_dict) > 0:
                            point = self.current_question.scores / len(matching_pairs_dict)
                        else:
                            point = 0

                        for key, value in self.request.POST.items():
                            if key.startswith('answer_'):
                                # Получаем наш левый и правый ответ
                                left_item = key.replace('answer_', '')
                                right_item = value

                                if left_item in matching_pairs_dict:
                                    expect_right = matching_pairs_dict[left_item]
                                    if right_item == expect_right:
                                        self.request.session['teacher_answers'] += point


                elif self.current_question.answer_type == 'SC':
                    if self.current_question.scores_for == Question.SCORE_FOR_ANSWER:
                        answer_dict = {
                            str(ids): score
                            for ids, score in self.current_question.answers.filter(is_correct=True).values_list('id', 'score')
                        }

                        # answer = list(self.current_question.answers.filter(is_correct=True).values_list('id', flat=True))
                        
                        student_answer = self.request.POST.get('answer')

                        if str(student_answer) in answer_dict:
                            print(answer_dict[student_answer])
                            self.request.session['teacher_answers'] += answer_dict[student_answer]

                    elif self.current_question.scores_for == Question.SCORE_FOR_QUESTION:
                        answer = self.current_question.answers.filter(is_correct=True).values_list('id', flat=True)
                        print(answer)

                        student_answer = form.cleaned_data.get('answer')

                        try:
                            if int(student_answer) in answer:
                                self.request.session['teacher_answers'] += self.current_question.scores
                        except ValueError as e:
                            print(e)


                elif self.current_question.answer_type == 'MC':
                    if self.current_question.scores_for == Question.SCORE_FOR_ANSWER:
                        answers_test_dict = {
                            str(ids): score 
                            for ids, score in  self.current_question.answers.filter(is_correct=True).values_list('id', 'score')
                        }
                        
                        students_answers = form.cleaned_data.get('answer')

                        for answer in students_answers:
                            if str(answer) in answers_test_dict:
                                print(answers_test_dict[answer])
                                self.request.session['teacher_answers'] += answers_test_dict[answer]

                    elif self.current_question.scores_for == Question.SCORE_FOR_QUESTION:
                        answers_tuple = tuple(self.current_question.answers.filter(is_correct=True).values_list('id', flat=True))
                        
                        # answers_list = self.current_question.answers.filter(is_correct=True).values_list('id', flat=True)

                        if len(answers_tuple) > 0:
                            point = self.current_question.scores / len(answers_tuple)
                        else:
                            point = 0

                        students_answers = form.cleaned_data.get('answer')

                        for answer in students_answers:
                            try:
                                if int(answer) in answers_tuple:
                                    self.request.session['teacher_answers'] += point
                            except ValueError as e:
                                print(e)
                                continue


                elif self.current_question.answer_type == 'INP':
                    if self.current_question.scores_for == Question.SCORE_FOR_ANSWER:
                        answers_dict = {
                            str(text).lower().strip(): score
                            for text, score in  self.current_question.answers.filter(is_correct=True).values_list('text', 'score')
                        }

                        get_student_answer = form.cleaned_data.get('answer', '')

                        if isinstance(get_student_answer, str):
                            student_answer = get_student_answer.lower().strip()
                        else:
                            student_answer = ''

                        if student_answer in answers_dict:
                            print(answers_dict[student_answer])
                            self.request.session['teacher_answers'] += answers_dict[student_answer]
                        else:
                            self.request.session['teacher_answers'] += self.current_question.scores / 2

                    elif self.current_question.scores_for == Question.SCORE_FOR_QUESTION:
                        answers_tuple = tuple(
                            str(text).lower().strip() for text in self.current_question.answers.filter(is_correct=True).values_list('text', flat=True))
                        
                        get_student_answer = str(form.cleaned_data.get('answer')).lower().strip()

                        if isinstance(get_student_answer, str):
                            student_answer = get_student_answer.lower().strip()
                        else:
                            student_answer = ''

                        if student_answer in answers_tuple:
                            self.request.session['teacher_answers'] += self.current_question.scores
                                       
                                       
                elif self.current_question.answer_type == 'AUD':
                    self.request.session['teacher_answers'] += self.current_question.scores / 2

        print(self.request.session['teacher_answers'], '/', self.current_question.scores)
        if self.request.session['question_index'] + 1 < len(self.request.session['test_review_session']):
            self.request.session['question_index'] += 1
        else:
            return redirect('tests:test_review_results')

        # question_index = self.request.session['question_index']
        # all_questions = self.request.session['test_review_session']
        # if question_index > len(all_questions):
        #     print('redirect 2')
        #     return redirect('app:index')
        
        return redirect('tests:take_test_review', test_id=self.kwargs['test_id'],  user_id=self.kwargs['user_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
            'current_question_group': self.current_question.group
        })
        return context

    


    

# class TakeTestReviewView(FormView):
#     template_name = 'tests/take_test_review.html'
#     form_class = TestReviewForm

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         user_id = self.kwargs.get('user_id')
#         test_id = self.kwargs.get('test_id')

#         user = get_object_or_404(User, id=user_id)
#         test = get_object_or_404(Tests, id=test_id)
#         review = get_object_or_404(TestsReviews, user=user, test=test)


#         kwargs.update({
#             'test': test,
#             'answers': review.answers,
#             'audio_answers': review.audio_answers or {}
#         })

#         self.review = review
#         self.test = test

#         return kwargs
    
#     def form_valid(self, form):
#         """
#         Логика обработки POST запроса, аналогична тому, что у тебя в POST методе в функциональном представлении.
#         """
#         correct_answers = 0.0
#         total_questions = len(self.test.questions.all())

#         for question in self.test.questions.all():
#             if question.question_type == 'MC':
#                 # Получаем правильные ответы
#                 correct_answer = question.answers.filter(is_correct=True)
#                 corrects = [i for i in correct_answer]

#                 selected_answer = form.cleaned_data.get(f'question_{question.id}_approve')
#                 selected_unpack = [int(i) for i in selected_answer]

#                 if len(corrects) > 1:
#                     points = 1 / len(corrects)
#                     for i in corrects:
#                         item = Answer.objects.filter(id=i.id).first()
#                         if item.id in selected_unpack:
#                             correct_answers += points

#                 elif len(corrects) == 1:
#                     for i in corrects:
#                         item = Answer.objects.filter(id=i.id).first()
#                         if item.id in selected_unpack:
#                             correct_answers += 1

#             elif question.question_type == "SC":
#                 correct_answer = question.answers.filter(is_correct=True).first()

#                 try:
#                     selected_answer = int(form.cleaned_data.get(f'question_{question.id}_approve')[0])
#                 except (IndexError, TypeError):
#                     selected_answer = None

#                 if correct_answer and correct_answer.id == selected_answer:
#                     correct_answers += 1

#             elif question.question_type == 'AUD':
#                 audio_response = form.cleaned_data.get(f'audio_answer_{question.id}_correct')

#                 if audio_response == True:
#                     correct_answers += 1

#             elif question.question_type == 'INP':
#                 selected_answer = form.cleaned_data.get(f'question_{question.id}_correct')
#                 if selected_answer == True:
#                     correct_answers += 1

#             elif question.question_type == 'MTCH':
#                 user_answers = form.cleaned_data.get(f"question_{question.id}_mtch")
#                 correct_pair = MatchingPair.objects.filter(question=question).count()
#                 scores = 1 / correct_pair
#                 correct_answers += scores * len(user_answers)

#         # Сохраняем изменения в аудио ответах
#         self.review.audio_answers = form.cleaned_data.get('audio_answers', self.review.audio_answers)
#         self.review.save()

#         # Считаем итоговый балл
#         score = correct_answers / total_questions * 100
#         print(f"Балл по тесту: {int(score)}%")

#         # Сохраняем результат
#         TestResult.objects.create(
#             user=self.review.user,
#             test=self.review.test,
#             score=score,
#             attempts=2,
#             duration=self.review.duration
#         )

#         # Удаляем review, так как тест завершен
#         self.review.delete()

#         # Перенаправляем пользователя после завершения теста
#         return redirect('users:profile')

#     def get_success_url(self):
#         """
#         Указываем URL, на который будет происходить перенаправление
#         """
#         return reverse_lazy('users:profile')
    

# def take_test_review(request, user_id, test_id):
#     user = get_object_or_404(User, id=user_id)
#     test = get_object_or_404(Tests, id=test_id)
#     review = get_object_or_404(TestsReviews, user=user, test=test)
#     answers = review.answers
#     audio_answers = review.audio_answers or {}


#     if request.method == 'POST':
#         form = TestReviewForm(test=test, answers=answers, data=request.POST)
#         if form.is_valid():
#             correct_answers = 0.0
#             total_questions = len(test.questions.all())

#             for question in test.questions.all():
#                 if question.question_type == 'MC':
                    
#                     # Получаем правильные ответы
#                     correct_answer = question.answers.filter(is_correct=True)
                    
#                     corrects = [i for i in correct_answer]

#                     # Получаем выбранные ответы учителем
#                     selected_answer = form.cleaned_data.get(f'question_{question.id}_approve')
#                     selected_unpack = [int(i) for i in selected_answer]
                    

#                     # TODO Реализовать стратегию позже 
#                     # multiple_choice_strategy = MultypleChoiceStrategy()
#                     # multiple_choice_strategy.calculate_point(question, selected_answer, correct_answer, form)


#                     if form.cleaned_data.get(f'question_{question.id}_approve'):
#                         # Если правильных ответов в вопросе несколько 
#                         if len(corrects) > 1:
#                             points = 1 / len(corrects)
#                             for i in corrects:
                                
#                                 item = Answer.objects.filter(id=i.id).first()
#                                 if item.id in selected_unpack:
#                                     correct_answers += points

#                         # Если один правильный ответ
#                         elif len(corrects) == 1:
#                             for i in corrects:
                                
#                                 item = Answer.objects.filter(id=i.id).first()
#                                 if item.id in selected_unpack:
#                                     correct_answers += 1

#                 elif question.question_type == "SC":
#                     correct_answer = question.answers.filter(is_correct=True).first()

#                     try:
#                         selected_answer = int(form.cleaned_data.get(f'question_{question.id}_approve')[0])
#                     except (IndexError, TypeError):
#                         selected_answer = None  # Если пользователь не выбрал ответ

#                     # Сравниваем ответ пользователя с правильным ответом
#                     if correct_answer and correct_answer.id == selected_answer:
#                         correct_answers += 1

#                 elif question.question_type == 'AUD':
#                     audio_response = form.cleaned_data.get(f'audio_answer_{question.id}_correct')

#                     if audio_response == True:
#                         correct_answers += 1                   
                
#                 elif question.question_type == 'INP':
#                     correct_answer = question.answers.filter(is_correct=True).first()


#                     selected_answer = form.cleaned_data.get(f'question_{question.id}_correct')

#                     if selected_answer == True:
#                         correct_answers += 1
#                 elif question.question_type == 'MTCH':
#                     user_answers = form.cleaned_data.get(f"question_{question.id}_mtch")
#                     correct_pair = MatchingPair.objects.filter(question=question).count()
#                     scores =  1 / correct_pair
#                     correct_answers += scores * len(user_answers)

#             review.audio_answers = audio_answers
#             review.save()

#             # TODO Переделать этот калл

#             # # Сохранение результата
#             score = correct_answers / total_questions * 100
#             print(f"Балл по тесту: {int(score)}%")

#             # # Создание TestResults и удаление TestReviews
#             TestResult.objects.create(user=review.user, test=review.test, score=score, attempts=2, duration=0)
#             review.delete()
#             return redirect('users:profile')

#     else:
#         form = TestReviewForm(test=test, answers=answers, audio_answers=audio_answers)

#     return render(request, 'tests/take_test_review.html', {'form': form, 'review': review, 'test': test, 'audio_answers': audio_answers})
    
class TestReviewResults(View):
    template_name = 'tests/test_review_results.html'

    def get(self, request, *args, **kwargs):
        correct_answers = self.request.session['teacher_answers']
        print(correct_answers)
        test_review_id = self.request.session['test_student_responses_id']
        if test_review_id:
            test_review = TestsReviews.objects.filter(id=test_review_id).select_related('user', 'test').first()
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
    
