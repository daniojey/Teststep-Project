# tests/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from users.models import User, UsersGroup, UsersGroupMembership
from .models import TestResult, Tests, Question, Answer
from .forms import TestForm, QuestionForm, AnswerForm, TestTakeForm

def index(request):
    return render(request, 'tests/index.html')


def rating(request):
    user = get_object_or_404(User, id=request.user.id)
    tests = Tests.objects.all()

    context = {
        'tests': tests,
        'user': user
    }

    return render(request, 'tests/rating.html', context)


def rating_test(request, test_id):
    test = Tests.objects.filter(id=test_id).first()

    user = get_object_or_404(User, id=request.user.id)
    
    user_group = UsersGroupMembership.objects.filter(user=user).first()

    if user_group:
        # Получаем всех пользователей, принадлежащих к той же группе, что и текущий пользователь
        group_members = UsersGroupMembership.objects.filter(group=user_group.group).order_by('user__username')
    else:
        # Если у пользователя нет группы, можно обработать этот случай по-своему
        group_members = []

    results = []
    for item in group_members:

        result = TestResult.objects.filter(user=item.user, test=test)
        results.append(result)

    
    context = {
        'test': test,
        'user': user,
        'results':results
    }


    return render(request, 'tests/rating_test.html', context=context)


def all_tests(request):
    if request.user.is_superuser:
        tests = Tests.objects.all()
    else:
        tests = Tests.objects.filter(user=request.user)


    return render(request, 'tests/all_tests.html', {'tests': tests})


@login_required
def create_test(request):
    if request.method == 'POST':
        form = TestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            test = form.save()
            return redirect('tests:add_questions', test_id=test.id)
    else:
        form = TestForm()
    return render(request, 'tests/create_test.html', {'form': form})


@login_required
def add_questions(request, test_id):
    test = get_object_or_404(Tests, pk=test_id)
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST, request.FILES)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.test = test  # Привязываем вопрос к текущему тесту
            question.save()
            return redirect('tests:add_questions', test_id=test.id)
    else:
        question_form = QuestionForm()
    
    questions = Question.objects.filter(test=test)

    return render(request, 'tests/add_questions.html', {
        'test': test,
        'question_form': question_form,
        'questions': questions
    })


def complete_questions(request, test_id):
    # После завершения добавления вопросов переходим на страницу с вопросами или на другую подходящую страницу
    return redirect('app:index')


@login_required
def add_answers(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    test = question.test
    questions = test.questions.all()
    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.question = question
            answer.save()
            return redirect('tests:add_answers', question_id=question.id)
    else:
        answer_form = AnswerForm()
    return render(request, 'tests/add_answer.html', {
        'test': test,
        'question': question,
        'questions': questions,
        'answer_form': answer_form
    })


def test_preview(request, test_id):
    if request.user.is_authenticated:
        test_results = request.user.test_results.all()
        test = get_object_or_404(Tests, id=test_id)
        user_test = TestResult.objects.filter(user=request.user, test=test)
        if len(user_test) > 0:
            if user_test[0].remaining_atemps > 0:
                test_required = True
            else:
                test_required = False
        else:
            test_required = True

    else:
        test_results = ['Для того чтобы пройти тест зарегестрируйтесь :D']

    test = get_object_or_404(Tests, pk=test_id)

    context = {
        "test": test,
        'test_results': test_results,
        'required_attemps': test_required,
    }

    return render(request, 'tests/test_preview.html', context=context)


def take_test(request, test_id):
    test = get_object_or_404(Tests, id=test_id)
    question = Question.objects.all()

    if request.method == 'POST':
        form = TestTakeForm(request.POST, test=test)
        if form.is_valid():
            # Сохраняем ответы в сессию
            request.session['test_responses'] = form.cleaned_data
            return redirect('tests:test_results', test_id=test_id)
        
    else:
        form = TestTakeForm(test=test)

    return render(request, 'tests/question.html', {'form': form, 'test': test, 'question': question})


def test_results(request, test_id):
    test = get_object_or_404(Tests, id=test_id)
    responses = request.session.get('test_responses', {})
    total_questions = test.questions.count()
    correct_answers = 0

    for key, value in responses.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            question = Question.objects.get(id=question_id)
            
            if question.question_type == 'SC':
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and correct_answer.id == int(value):
                    correct_answers += 1
            elif question.question_type == 'MC':
                correct_answers_list = question.answers.filter(is_correct=True).values_list('id', flat=True)
                if set(map(int, value)) == set(correct_answers_list):
                    correct_answers += 1
            elif question.question_type == 'IMG':
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and correct_answer.id == int(value):
                    correct_answers += 1
            elif question.question_type == 'AUD':
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and correct_answer.id == int(value):
                    correct_answers += 1
            elif question.question_type == 'MTCH':
                ... # Реализовать позже


    score = (correct_answers / total_questions) * 100
    score = round(score)

    if request.user.is_authenticated:
        test_result, created = TestResult.objects.get_or_create(
            user=request.user,
            test=test,
            defaults={'score': score, 'attempts': 1}
        )
        
        if not created:
            print(test_result)
            if test_result.remaining_atemps > 0:
                test_result.attempts += 1
                test_result.score = max(test_result.score, score)  # Сохраняем лучший результат
                test_result.save()
            else:
                return render(request, 'tests/test_limit_reached.html')
            
    context = {
        'test': test,
        'score': score,
        'correct_answers': correct_answers,
        'total_questions': total_questions
    }
    
    return render(request, 'tests/test_results.html', context)
