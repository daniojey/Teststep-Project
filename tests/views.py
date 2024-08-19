# tests/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import TestResult, Tests, Question, Answer
from .forms import TestForm, QuestionForm, AnswerForm, TestTakeForm

def index(request):
    return render(request, 'tests/index.html')


def rating(request):
    return render(request, "tests/rating.html")


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
    test_results = request.user.test_results.all()
    test = get_object_or_404(Tests, pk=test_id)

    context = {
        "test": test,
        'test_results': test_results,
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

    score = (correct_answers / total_questions) * 100
    score = round(score)
    context = {
        'test': test,
        'score': score,
        'correct_answers': correct_answers,
        'total_questions': total_questions
    }
    
    if request.user.is_authenticated:
        TestResult.objects.create(user=request.user, test=test, score=round(score, 2))
    
    return render(request, 'tests/test_results.html', context)