# tests/views.py
import random
from django.db.models import F, ExpressionWrapper, Prefetch, fields
from django.forms import ClearableFileInput, DateInput, Textarea
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import localtime, now
from django.urls import reverse, reverse_lazy
from django.views import View

from common.mixins import CacheMixin
from users.models import User, UsersGroupMembership
from .models import Categories, MatchingPair, QuestionGroup, TestResult, Tests, Question, Answer, TestsReviews
from .forms import MatchingPairForm, QuestionGroupForm, QuestionStudentsForm, TestForm, QuestionForm, AnswerForm, TestReviewForm, TestTakeForm
from django.core.files.base import ContentFile
from django.views.generic import FormView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
import base64
import os
from django.core.files.storage import default_storage
from datetime import timedelta

def index(request):
    return render(request, 'tests/index.html')

class UserRatingView(LoginRequiredMixin, TemplateView):
    """
    Displays the page where tests for which there are already 
    results from other group members are posted.

    This view will display for the average user a page with tests for which he has a result, 
    and for the teacher will display all the tests that he has created.

    Attributes
    ----------
    template_name : str
        The path to the template user for rendering rating page.

    Methods
    -------
    get_context_data(**kwargs)
        In this method, we get information about(tests, user, group, active_tab)
    """

    template_name = 'tests/rating.html'

    def get_context_data(self, **kwargs):
        """
        Retrieves and adds data to the context for rendering the rating page.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments passed to the view.

        Returns
        -------
        dict
            A dictionary containing the following keys:
            - 'tests' : QuerySet of tests filtered by the user's role in the group (either teacher or student).
            - 'group' : The name of the group. If the user is not part of a group, it returns None.
            - 'active_tab' : Used to highlight the active tab in the navigation menu (affects link styling in `base.html`).
        """

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
    """
    This view renders the rating_test page

    This page will draw a table with the result of users on the test that was selected on the rating page 

    Attributes
    ----------
    template_name : str
        This variable contains the path to the rating_test page

    Methods
    -------
    get_context_data(**kwargs)
        This method retrieves data(test, user, results, active_tab)
    """
    template_name = "tests/rating_test.html"

    def get_context_data(self, **kwargs):
        """
        This method retrieves data to be passed to rating_test

        Parametrs
        ---------
        **kwargs : dict
            Additional keyword arguments passed to the view.

        Returns
        -------
        dict
            The following keys are passed in this dictionary
            - 'test' : The test object is transferred.
            - 'results': Queryset which contains test results (TestsResult model),
            user,test,score,duration these parameters will be used in the template, 
            if the user is not in the group we pass an empty list.
            - 'active_tab' : Used to highlight the active tab in the navigation menu (affects link styling in `base.html`).
        """
        
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, id=self.request.user.id)
        test_id = self.kwargs.get('test_id')


        test = get_object_or_404(Tests, id=test_id)
        user_group = UsersGroupMembership.objects.filter(user=user).select_related('group').first()


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
    """
    This view renders the all_tests page

    This page contains tests created by the teacher of the group,
    all the tests are displayed for the administrator.

    Attributes
    ----------
    template_name : str
        This variable contains the path to all_tests page

    Methods
    -------
    get_context_data(**kwargs)
        This method retriever data(tests)
    """

    template_name = "tests/all_tests.html"

    def get_context_data(self, **kwargs):
        """
        This method retrives data to all_tests page
        
        Parametrs
        ---------
        **kwargs : dict
            Additional keyword arguments passed to the view

        Returns
        -------
        dict
            The following keys are passed in this dictionary
            - 'tests': QuerySet where the filtered tests are located
            - 'active_tab': Used to highlight the active tab in the navigation menu (affects link styling in `base.html`).
        """

        context = super().get_context_data(**kwargs)

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
    # TODO Обновить доку в ближайшее время
    """
    Handles the creation of tests by teachers.

    Attributes:
    ----------
    template_name : str
        Path to the HTML template for rendering the test creation page.
    form_class : Form instance
        The form class used to collect test data(tests.forms.TestForm, line=9).

    Methods:
    -------
    get_form_kwargs()
        Adds the current user to the form context.
    form_valid(form)
        Creates and saves a new test instance if the form data is valid.
    form_invalid(form)
        Renders the form page with validation errors for user correction.
    get_context_data(**kwargs)
        Adds additional context variables (e.g., active link) to the template.
    get_success_url()
        Returns the URL for redirecting upon successful form submission.
    """

    template_name = 'tests/create_test.html'
    form_class = TestForm

    def get_form_kwargs(self):
        """
        Returns the current user to the form

        Returns
        -------
        - 'user': Current user
        """

        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """
        Processes the validated form data to create and save a test instance.

        Parameters
        ----------
        form : Form instance
            The validated form filled out by the user.

        Returns
        -------
        HttpResponseRedirect
            A redirect to the success URL, as defined in the `get_success_url` method.

        Notes
        -----
        - The `super().form_valid(form)` method is called to handle the redirection logic.
        - The `get_success_url` method from the parent class (`FormView`) is used to determine the redirect destination.
        - Before calling the parent method, this implementation saves additional data (e.g., test duration, user, and selected students) to the `Tests` model instance.
        """

        test = form.save(commit=False)
        test.user = self.request.user

        # Обработка студентов
        selected_students = form.cleaned_data.get('students')
        test.students = {'students': selected_students}


        # Обработка длительности
        test.duration = form.cleaned_data.get('raw_duration')
        test.save()

        self.object = test
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Returns an invalid form to handle errors in the template
        """
        # Сбор ошибок формы
        errors = []
        # Общие ошибки формы
        if form.non_field_errors():
            errors.extend(form.non_field_errors())
        # Ошибки полей
        for field, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(f"- {error}")

        # Передаем ошибки в шаблон
        return self.render_to_response({'form': form, 'errors': errors})
    
    
    def get_context_data(self, **kwargs):
        """
        This method returns to the data in the template context

        Returns
        -------
        dict
          - 'active_link':sed to highlight the active link in the navigation menu (affects link styling in `base.html`).
        """
        context = super().get_context_data(**kwargs)
        context['active_link'] = 'create'
        return context
    
        
    def get_success_url(self) -> str:
        """
        Returns
        ------- 
        Url to redirect to the add questions page after creating a quiz
        """

        return reverse('tests:add_questions', kwargs={'test_id': self.object.id})
    

class EditTestView(UpdateView):
    # TODO Добарботать документатцию этого придеставления

    """
    Edit test view.

    Attributes
    ----------
    model : Model Object
        Refers to the Tests model, which is located at tests.models.Tests (line=18).
    template_name : str
        Path to the HTML tamplate for rendering the test edit page.
    fields: list['str']
        Contains the names of fields from the Tests model that will be passed to the form so that they can be modified.
    success_url : url path
        Contains the url path to which the user will be redirected after successful test change, the url specified in success_url can be viewed in tests.urls (line=15).
    """
    model=Tests
    template_name = "tests/edit_test.html"
    fields = ['name', 'description','image', 'date_out', 'category', 'check_type']

    def form_valid(self, form):
        print("Submitted date:", form.cleaned_data['date_out'])
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
        
        form = super().get_form(form_class)
        print("Original date_out:", self.object.date_out)  # Дата из объекта
        print("Formatted date_out:", self.object.date_out.strftime('%Y-%m-%d'))  # Отформатированная дата
        
        form.fields['description'].widget = Textarea(attrs={'rows': 4})
        form.initial['image'] = None
        form.fields['image'].widget = ClearableFileInput(attrs={
            'class': 'form-image-field',  # Класс для стилизации
            'data-no-file-text': 'Оберіть фото',  # Можно добавить атрибуты, если нужно
            'id': 'uploadImage'
        })

        form.fields['category'].choices = [(item.id, item.name) for item in Categories.objects.all()]

        form.fields['date_out'].widget = DateInput(
            attrs={'type': 'date', 'class': 'date-wrapper'}
        )

        if self.object.date_out:
            # Преобразуем дату в локальную таймзону
            local_date = localtime(self.object.date_out).date()
            form.initial['date_out'] = local_date.strftime('%Y-%m-%d')
            print("Local date_out for form:", local_date)
        return form
    
    def get_success_url(self):
        # Correct way to pass pk as an argument
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
    # messages.success(request, 'Тест успешно удалён!')
    return redirect('app:index')


class AddQuestionGroupView(LoginRequiredMixin, FormView):
    """
    The view is used to create a group for the questions in the test 

    Attributes
    ----------
    template_name : str
        Path to the HTML template for rendering the add question group page
    form_class : Form instance
        The form class used to collect test data(tests.forms.QuestionGroupForm, line=125)
    
    Methods
    -------
    form_valid(form)
        Saves the question group for the test if the form is valid
    """

    template_name = 'tests/adq.html'
    form_class = QuestionGroupForm

    def form_valid(self, form):
        """
        Processes the validated form data to create and save a question group instance

        Parameters
        ----------
        form : Form instance
            The validated form filled out by the user
        
        Returns
        -------
        HttpResponseRedirect
            Redirects to the url specified in the redirect function,
            also passes test.id required for the specified url (path to url tests.urls, line=18).
        """
        test_id = self.kwargs.get('test_id')
        test = get_object_or_404(Tests, id=test_id)

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
    """
    This view is used to create questions for tests, 
    also 2 forms are used here, the form for adding 
    questions and the form for adding students to the test

    Attributes
    ----------
    template_name : str
        Path to the HTML tempalte for rendering the add question page.

    Methods
    -------
    get_context_data(**kwargs)
        Adds additional context variables (test, question_groups, ungrouped_questions,question_form, form_student)
    post(*args, **kwargs)

    """

    template_name = 'tests/add_questions.html'

    def get_context_data(self, **kwargs):
        """
        This method returns to the data in the tamplate context

        Returns
        -------
        dict
          A dictionary containing the following keys:
          - 'test': returns Object test
          - 'question_groups': Queryset which returns questions that are in groups of questions.
          - 'ungrouped_questions': a Queryset that contains questions not supported by any of the question groups.
          - 'question_form': Question creation form (this form can be viewed at tests.forms.QuestionForm, line=135).
          - 'form_student': Form for selecting students from the group in which the teacher is a member.
        """
        context = super().get_context_data(**kwargs)
        test_id = self.kwargs.get('test_id')

        # Получаем тест с минимальным количеством запросов
        test = get_object_or_404(Tests.objects.select_related('user'), id=test_id)
        user = self.request.user

        
        # Заранее загружаем все вопросы, связаные с тестом
        questions = Question.objects.filter(test=test).select_related('group')


        # Группы вопросов с предзагрузкой вопросов
        question_groups = (
            QuestionGroup.objects.filter(test=test).prefetch_related(
                Prefetch('questions_group', queryset=questions)
            )
        )
        
        # print(question_groups)
        # for group in question_groups:
        #     print(group)
        #     for question in group.questions_group.all():
        #         print(question)

        # заранее фильтруем вопросы без группы
        ungrouped_questions = [q for q in questions if q.group is None]


        # Формы
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
        """
        Handles post requests sent from the client, 
        forms from which post requests to this view may be received:
        (the path to both forms is the same, tests.forms)
        QuestionForm - line 135
        QuestionStudentsForm - line 197

        Parameters
        ----------
        request : HttpRequest
            the HTTP request object containing form data.
        *args : tuple
            Additional positional arguments
        **kwargs : dict
            Additional keyword arguments, including 'test_id'.

        Returns
        -------
        HttpResponse
            - On successful processing of the `QuestionForm`, redirects to the add questions page.
            - On successful processing of the `QuestionStudentsForm`, returns a JSON response with status "success."
            - If the forms are invalid, re-renders the page with errors displayed in the context.

        Behavior
        --------
        - Determines the form type (`form_question` or `form_student`) based on the `form_type` field in the POST data.
        - Validates the submitted form:
          - If `QuestionForm` is valid, saves the question and associates it with the test.
          - If `QuestionStudentsForm` is valid, updates the test's student information and saves it.
        - If a form is invalid, errors are logged and displayed to the user.

        Side Effects
        ------------
        - Saves the question to the database if `QuestionForm` is valid.
        - Updates the test's `students` field if `QuestionStudentsForm` is valid.

        Notes
        -----
        - The context for re-rendering the page includes updated forms and their validation states.
        - If the `form_type` is not recognized, the method falls back to re-rendering the page with context data.

        Examples
        --------
        Submitting a question form:
        >>> POST data: {'form_type': 'form_question', 'question_text': 'Sample question', ...}
        Redirects to 'tests:add_questions' with the test ID.

        Submitting a student form:
        >>> POST data: {'form_type': 'form_student', 'students': ['1', '2'], ...}
        Returns: {"status": "success", "message": "Студенты обновлены."}
        """
        
        test_id = self.kwargs.get('test_id')
        test = get_object_or_404(Tests, id=test_id)
        user = request.user

        form_type = request.POST.get('form_type')

        question_form = QuestionForm(request.POST, request.FILES, test=test)
        students_form = QuestionStudentsForm(request.POST, request.FILES, test=test, user=user)

        if form_type == 'form_question':
            if question_form.is_valid():
                question = question_form.save(commit=False)
                question.test = test
                question.save()
                return redirect('tests:add_questions', test_id=test.id)
            else:
                # Сбор ошибок формы
                errors = []
                # Общие ошибки формы
                if question_form.non_field_errors():
                    errors.extend(question_form.non_field_errors())
                # Ошибки полей
                for field, field_errors in question_form.errors.items():
                    for error in field_errors:
                        errors.append(f"- {error}")

                # Передаем ошибки и форму в контекст
                context = self.get_context_data(test_id=kwargs.get('test_id'))
                context['form_question'] = question_form
                context['errors'] = errors
            
                # Возвращаем обновленный контекст с ошибками
                return self.render_to_response(context)
            
        elif form_type == 'form_student':
            if students_form.is_valid():
                test.students = {'students': students_form.cleaned_data.get('students')}
                test.save()
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
    # После завершения добавления вопросов переходим на страницу с вопросами или на другую подходящую страницу
    return redirect('app:index')


class AddAnswersView(LoginRequiredMixin, FormView):
    template_name = 'tests/add_answer.html'
    form_class = AnswerForm

    def form_valid(self, form):
        print(self.request.POST)
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=question_id)

        answer = form.save(commit=False)
        answer.question = question
        answer.save()
        return redirect('tests:add_answers', question_id=question.id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(
            Question.objects.select_related('test').prefetch_related('answers'),
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
        print(request.POST)
        question = get_object_or_404(Question.objects.prefetch_related('answers'), id=self.kwargs['question_id'])

        correct_answers_ids = request.POST.getlist('correct_answers')
        if question.answer_type == 'SC':
            question.answers.all().update(is_correct=False)
            if correct_answers_ids:
                id_answer = correct_answers_ids[0]
                answer = Answer.objects.filter(id=id_answer).update(is_correct=True)
            

        elif question.answer_type == 'MC':
            question.answers.all().update(is_correct=False)
            answers = Answer.objects.filter(id__in=correct_answers_ids).update(is_correct=True)
            print(answers)
        else:
            # INP и MTCH не трогаем так как сохраняется всё коректно по умолчанию
            ...
        # answer = Answer.objects.get(id=correct_answers_ids[0])
        # print(answer)
        # print(answer.is_correct)

        # for item_id in correct_answers_ids:
        #     print(f"Type{type(item_id)} and id {item_id}")
        #     print(get_object_or_404(Answer, id=item_id))
        print(correct_answers_ids)

        return redirect(reverse('tests:add_questions', args=[question.test.id]))


def delete_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    question = get_object_or_404(Question, id=answer.question.id)
    
    answer.delete()
    return redirect('tests:add_answers', question_id=question.id)


class AddMathicngPairView(LoginRequiredMixin, FormView):
    template_name = 'tests/add_answer.html'
    form_class = MatchingPairForm

    def form_valid(self, form):
        question_id = self.kwargs.get('question_id')
        question = get_object_or_404(Question, id=question_id)

        answer = form.save(commit=False)
        answer.question = question
        answer.save()

        return redirect('tests:add_matching_pair', question_id=question.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_id = self.kwargs.get('question_id')

        question = get_object_or_404(
            Question.objects.select_related('test').prefetch_related('test__questions'),
            id=question_id
        )

        test = question.test
        questions = test.questions.all()
        matching_pairs = MatchingPair.objects.filter(question=question)
        # print(matching_pairs)
        # print(question.matching_pairs.all())

        # context['test'] = test
        # context['question'] = question
        # context['questions'] = questions
        # context['form_type'] = 'Соотвецтвие'
        # context['action_url'] = 'tests:add_matching_pair'

        context.update({
            'test': test,
            'question': question,
            'group': question.group,
            'questions': questions,
            'form_type': 'Соотвецтвие',
            'action_url': 'tests:add_matching_pair'
        })

        return context
    
def delete_matching_pair(request, pair_id):
    # print(pair_id)
    matching_pair = get_object_or_404(MatchingPair, id=pair_id)
    question = get_object_or_404(Question, id=matching_pair.question.id)

    # print(f"pair:{matching_pair}")
    # print(f"question: {question}")
    print(question)
    print(matching_pair)
    matching_pair.delete()
    return redirect('tests:add_matching_pair', question_id=question.id)

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

class TestPreviewView(TemplateView):
    template_name = 'tests/test_preview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        test_id = self.kwargs.get('test_id')

        if self.request.user.is_authenticated:
            # test_results = user.test_results.all()
            test = get_object_or_404(Tests.objects.select_related('user'), id=test_id)
            test_results = TestResult.objects.filter(test=test, user=user).select_related('test', 'user').first()
            test_review = TestsReviews.objects.filter(user=user, test=test).select_related('test', 'user')
            user_test = TestResult.objects.filter(user=user).select_related('test')
            if len(user_test) > 0:
                if user_test[0].remaining_atemps > 0:
                    test_required = True
                else:
                    test_required = False
            else:
                test_required = True
        else:
            test_results = ['Для того чтобы пройти тест зарегестрируйтесь :D']
            test_review = ['None']
        
        test = get_object_or_404(Tests, id=test_id)

        context.update({
            'test': test,
            'test_results': test_results,
            'required_attemps': test_required,
            'test_review': test_review,
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


class TakeTestView(FormView):
    template_name = 'tests/question.html'
    form_class = TestTakeForm

    def dispatch(self, request, *args, **kwargs):
        # Сохраняем test_id в сессию
        self.test = get_object_or_404(Tests, id=self.kwargs['test_id'])

        # Очищаем сессию перед созданием новой для теста
        print(self.test.id, "ID теста который Был запущен")
        print(request.session.get('test_id'), "ID теста который уже в сессии")

        session_test_id = request.session.get('test_id')
        if self.test.id != session_test_id and session_test_id != None:
            self.clear_test_session(request=request)

        request.session['test_id'] = self.test.id


        # Сохраняем время начала теста, если оно ещё не сохранено
        if 'test_start_time' not in request.session:
            request.session['test_start_time'] = now().timestamp()  # Сохраняем метку времени

        # Инициализируем таймер, если тест только начался
        if 'remaining_time' not in request.session:
            request.session['remaining_time'] = self.test.duration.total_seconds()

        # Инициализация сессии для теста
        if 'question_order' not in request.session:
            response = self.initialize_test_session()
            if isinstance(response, HttpResponse):
                return response

        return super().dispatch(request, *args, **kwargs)

    def clear_test_session(self, request):
        """Очищает данные теста из сессии."""
        print("Очистка сессии в представлении")
        keys_to_clear = ['test_id', 'question_order', 'question_index', 'test_responses', 'remaining_time', 'test_start_time']
        for key in keys_to_clear:
            if key in request.session:
                del request.session[key]

    def initialize_test_session(self):
        # Получаем вопросы, отсортированные по группам
        questions_by_group = {}
        for group in QuestionGroup.objects.filter(test=self.test).prefetch_related('questions_group'):
            questions_by_group[group.name] = list(group.questions_group.all())

        # Перемешиваем вопросы внутри каждой группы
        for group_name, questions in questions_by_group.items():
            random.shuffle(questions)

        # Объединяем все перемешанные вопросы в один список
        all_questions = []
        for questions in questions_by_group.values():
            all_questions.extend(questions)

        # Добавляем вопросы без группы
        questions_not_group = list(Question.objects.filter(test=self.test, group=None))
        random.shuffle(questions_not_group)
        all_questions.extend(questions_not_group)

        if len(all_questions) == 0:
            # Очищаем сессию дабы избежать конфликтов
            if 'test_id' in self.request.session:
                del self.request.session['test_id']

            if 'remaining_time' in self.request.session:
                del self.request.session['remaining_time']

            if 'test_start_time' in self.request.session:
                del self.request.session['test_start_time']


            return redirect('app:index')
        else:
            # Сохраняем порядок вопросов в сессии
            self.request.session['question_order'] = [q.id for q in all_questions]
            self.request.session['question_index'] = 0  # Начинаем с первого вопроса
            self.request.session['test_responses'] = {}  # Для хранения ответов

    def get_form_kwargs(self):
        # Передаем текущий вопрос в форму
        kwargs = super().get_form_kwargs()
        question_order = self.request.session['question_order']
        question_index = self.request.session['question_index']
        current_question_id = question_order[question_index]
        self.current_question = get_object_or_404(Question.objects.select_related('group'), id=current_question_id)
        # print(self.current_question.test)
        # print(self.current_question.question_type)
        # print(self.current_question.answer_type)
        # print(self.current_question)

        kwargs['question'] = self.current_question
        return kwargs

    def form_valid(self, form):
        answer = form.cleaned_data.get('answer')

        # Обрабатываем разные типы вопросов
        if self.current_question.question_type == 'AUD' or self.current_question.question_type == 'IMG' or self.current_question.question_type == 'TXT':
            if self.current_question.answer_type == 'AUD':
                audio_answer = form.cleaned_data.get(f'audio_answer_{self.current_question.id}', None)
                print(f"AUDIO_ANSWER_GET:{audio_answer}")
                print(f"POST:{self.request.POST}")
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

            # На данный момент резервный путь для того чтобы тесты точно попадали в обработку
            if answer:
                self.request.session['test_responses'][f"question_{self.current_question.id}"] = answer

        # Обновляем оставшееся время
        remaining_time = int(self.request.POST.get('remaining_time', 0))
        self.request.session['remaining_time'] = remaining_time

        # Переход к следующему вопросу
        self.request.session['question_index'] += 1

        # Проверка, не завершен ли тест
        question_order = self.request.session['question_order']
        question_index = self.request.session['question_index']
        if question_index >= len(question_order):
            return redirect('tests:test_results', test_id=self.kwargs['test_id'])

        return redirect('tests:take_test', test_id=self.kwargs['test_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_order = self.request.session['question_order']
        question_index = self.request.session['question_index']
        # context['test'] = self.test
        # context['question'] = self.current_question
        # context['all_questions'] = {
        #     "current": question_index + 1,
        #     "all": len(question_order)
        # }
        # context['test_btn'] = {
        #     'text_btn': 'Завершити' if question_index + 1 == len(question_order) else 'Далі',
        # }
        # context['current_question_group'] = self.current_question.group
        # context['remaining_time'] = self.request.session['remaining_time']

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

            # На случай если пользователь перезагрузил страницу при ручном тесте
            if not test_time:
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

            # На случай если пользователь перезагрузил страницу
            if not test_time:
                return redirect('app:index')
            
            score, correct_answers, total_questions, test_duration = self.calculate_results(test, responses, test_time)
            self.save_test_results(request, test, score, test_duration)
            self.clear_test_session(request)
            context = self.get_context_data(test, score, correct_answers, total_questions)
            return render(request, self.template_name, context)
        
    def save_audio_responses(self, request, responses, audio_answers):
        """Сохраняем аудио ответы из сессии"""
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
        """Вычисляем результаты теста."""
        total_questions = test.questions.count()
        correct_answers = 0.0


        for key, value in responses.items():
            if key.startswith('question_'):
                question_id = int(key.split('_')[1])
                question = Question.objects.get(id=question_id)
                correct_answers += self.evaluate_question(question, value)

        
        score = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        test_duration = timedelta(seconds=test.duration.total_seconds() - test_time)

        return score, int(correct_answers), total_questions, test_duration

    def evaluate_question(self, question, value):
        """Оценка вопроса на основе типа"""
        correct_answers = 0.0

        if question.question_type == 'TXT':
            if question.answer_type == 'SC':
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and correct_answer.id == int(value):
                    correct_answers += 1.0

            elif question.answer_type == 'MC':
                correct_answers_list = list(question.answers.filter(is_correct=True).values_list('id', flat=True))
                # print(correct_answers_list)
            
                # # Преобразуем ответы пользователя к целым числам и сравниваем с правильным списком
                if set(map(int, value)) == set(correct_answers_list):
                    correct_answers += 1.0

            elif question.answer_type == 'INP':
                correct_answer = question.answers.filter(is_correct=True).first()
                if str(correct_answer).strip().lower() == str(value).strip().lower():
                    correct_answers += 1.0

        # if question.question_type == 'SC':
        #     correct_answer = question.answers.filter(is_correct=True).first()
        #     if correct_answer and correct_answer.id == int(value):
        #         correct_answers += 1.0
        # elif question.question_type == 'MC':
        #     correct_answers_list = list(question.answers.filter(is_correct=True).values_list('id', flat=True))
        #     print(correct_answers_list)
            
        #     # # Преобразуем ответы пользователя к целым числам и сравниваем с правильным списком
        #     if set(map(int, value)) == set(correct_answers_list):
        #         correct_answers += 1.0
        elif question.question_type == 'IMG':
            if question.answer_type == 'SC':
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and correct_answer.id == int(value):
                    correct_answers += 1.0

            elif question.answer_type == 'MC':
                correct_answers_list = list(question.answers.filter(is_correct=True).values_list('id', flat=True))
                # print(correct_answers_list)
            
                # # Преобразуем ответы пользователя к целым числам и сравниваем с правильным списком
                if set(map(int, value)) == set(correct_answers_list):
                    correct_answers += 1.0

            elif question.answer_type == 'INP':
                correct_answer = question.answers.filter(is_correct=True).first()
                if str(correct_answer).strip().lower() == str(value).strip().lower():
                    correct_answers += 1.0

        elif question.question_type == 'AUD':
            if question.answer_type == 'SC':
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and correct_answer.id == int(value):
                    correct_answers += 1.0

            elif question.answer_type == 'MC':
                correct_answers_list = list(question.answers.filter(is_correct=True).values_list('id', flat=True))
                # print(correct_answers_list)
            
                # # Преобразуем ответы пользователя к целым числам и сравниваем с правильным списком
                if set(map(int, value)) == set(correct_answers_list):
                    correct_answers += 1.0

            elif question.answer_type == 'INP':
                correct_answer = question.answers.filter(is_correct=True).first()
                if str(correct_answer).strip().lower() == str(value).strip().lower():
                    correct_answers += 1.0
        # elif question.question_type == "INP":
        #     correct_answer = question.answers.filter(is_correct=True).first()
        #     if str(correct_answer).strip().lower() == str(value).strip().lower():
        #         correct_answers += 1.0
        elif question.question_type == 'MTCH':
                questions_count = MatchingPair.objects.filter(question=question).count()
                points = 1 / questions_count
                for left, right in value.items():
                    if MatchingPair.objects.filter(question=question, left_item=left, right_item=right).exists():
                        correct_answers += points

        return correct_answers
    
    def save_test_results(self, request, test, score, test_duration):
        """Сохраняем результаты теста пользователя"""
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
        """Очищаем данные теста из сессии"""
        session_keys = ['question_order','question_index','test_responses','remaining_time', 'test_id']
        for key in session_keys:
            if key in request.session:
                del request.session[key]

    def get_context_data(self, test, score, correct_answers, total_questions):
        """Подготовка данных для шаблона"""
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
    template_name = 'tests/tr.html'

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

        # Получаем всех членов группы и название группы
        group_memberships, group_name = self.get_user_group(user=user)

        user_reviews = []

        # Здесь мы можем сразу выбрать нужные данные
        reviews_qs = TestsReviews.objects.filter(test=test).select_related('user')

        for us in group_memberships:
            review = reviews_qs.filter(user=us.user).first()
            if review:    
                user_reviews.append(review)

        # context['test'] = test
        # context['user_reviews'] = user_reviews

        context.update({
            'test': test,
            'user_reviews': user_reviews
        })


        return context

    def get_user_group(self, user):
        user_group = UsersGroupMembership.objects.filter(user=user).select_related('group').first().group
        
        if user_group:
            group_memberships = UsersGroupMembership.objects.filter(group=user_group).select_related('group')
            group_name = user_group.name
        else:
            group_memberships = None
            group_name = None

        return group_memberships, group_name

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
        
         # Проверяем, если сессия не содержит необходимых данных, пересоздаем её
        required_keys = ['teacher_answers', 'test_review_session', 'question_index', 'teacher_responses', 'test_student_responses_id']
        
        missing_keys = [key for key in required_keys if key not in request.session]
        print(missing_keys)
        
        if missing_keys:
            # Если какие-то ключи отсутствуют, пересоздаем сессию
            self.initialize_session_test()

        return super().dispatch(request, *args, **kwargs)

    def initialize_session_test(self):
        questions = Question.objects.filter(test=self.test)

        if len(questions) == 0:
            # Вариант: перенаправление или сообщение об ошибке
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

        # print(current_question_id)
        # print(self.test_student_responses.answers)
        # Получение ответа на основе типа вопроса
        if self.current_question.answer_type == 'AUD':
            self.current_students_question = self.test_student_responses.audio_answers.get(f'audio_answer_{current_question_id}', [])
        elif self.current_question.question_type == 'MTCH':
            self.current_students_question = self.test_student_responses.answers.get(f'question_{current_question_id}_type_matching', [])
        else:
            self.current_students_question = self.test_student_responses.answers.get(f'question_{current_question_id}', [])

        # print(self.current_students_question)

        kwargs['audio_answers'] = self.test_student_responses.audio_answers
        kwargs['question'] = self.current_question
        kwargs['student_question'] = self.current_students_question
        return kwargs

    def form_valid(self, form):

        if self.request.method == 'POST':
            action = self.request.POST.get('action')
            if action == 'correct':
                self.request.session['teacher_answers'] += 1.0

            elif action == 'incorrect':
                # Ответ неверный поэтому ничего не добавляем
                print('incorrect')

            # добавляем автоматическую обработку для каждого пита ответа если 
            elif action == 'partial':
                if self.current_question.question_type == 'MTCH':
                    matching_pairs = list(self.current_question.matching_pairs.all())

                    left_items = [pair.left_item for pair in matching_pairs]
                    point = 1 / len(left_items) if len(left_items) > 0 else 0

                    for left_item in left_items:
                        student_answer = self.request.POST.get(f'answer_{left_item}')
                        if any(pair.left_item == left_item and pair.right_item == student_answer for pair in matching_pairs):
                                self.request.session['teacher_answers'] += point


                elif self.current_question.answer_type == 'SC':
                    answer = list(self.current_question.answers.filter(is_correct=True).values_list('id', flat=True))
                    
                    student_answer = int(self.request.POST.get('answer'))

                    if student_answer in answer:
                        self.request.session['teacher_answers'] += 1.0


                elif self.current_question.answer_type == 'MC':
                    answers_test = list(Answer.objects.filter(question=self.current_question, is_correct=True).values_list('id', flat=True))

                    answers = self.current_question.answers.filter(is_correct=True).values_list('id', flat=True)
                    point = 1 / len(answers) if len(answers) > 0 else 0
                    
                    students_answers = form.cleaned_data.get('answer')

                    for answer in students_answers:
                        if int(answer) in answers_test:
                            self.request.session['teacher_answers'] += point


                elif self.current_question.answer_type == 'INP':
                    answers = self.current_question.answers.filter(is_correct=True).values_list('text', flat=True)
                    answers = [answer.lower() for answer in answers]

                    student_answer = form.cleaned_data.get('answer')

                    if student_answer.lower() in answers:
                        self.request.session['teacher_answers'] += 1.0
                    else:
                        self.request.session['teacher_answers'] += 0.5
                                       
                                       
                elif self.current_question.answer_type == 'AUD':
                    self.request.session['teacher_answers'] += 0.5


         # Увеличиваем индекс вопроса только если он не выходит за пределы
        if self.request.session['question_index'] + 1 < len(self.request.session['test_review_session']):
            self.request.session['question_index'] += 1
        else:
            # print('redirect 1')
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
        # context['test'] = self.test
        # context['user'] = self.user
        # context['question'] = self.current_question
        # context['all_questions'] = {
        #     "current": question_index + 1,
        #     "all": len(test_review_session)
        # }

        # context['current_question_group'] = self.current_question.group
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
        test_review_id = self.request.session['test_student_responses_id']
        if test_review_id:
            test_review = TestsReviews.objects.filter(id=test_review_id).select_related('user', 'test').first()
        else:
            test_review = None

        if test_review:
            user = test_review.user
            test = test_review.test
            duration = test_review.duration
            questions = test.questions.count()

        

            score = round((correct_answers / questions) * 100) if questions > 0 else 0
            print(score)
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
    