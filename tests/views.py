# tests/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Tests, Question, Answer
from .forms import TestForm, QuestionForm, AnswerForm

def index(request):
    return render(request, 'tests/index.html')

def rating(request):
    return render(request, "tests/rating.html")

def all_tests(request):
    tests = Tests.objects.all()
    return render(request, 'tests/all_tests.html', {'tests': tests})


def create_test(request):
    if request.method == 'POST':
        form = TestForm(request.POST, request.FILES)
        if form.is_valid():
            test = form.save()
            return redirect('tests:add_questions', test_id=test.id)
    else:
        form = TestForm()
    return render(request, 'tests/create_test.html', {'form': form})

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
    test = get_object_or_404(Tests, pk=test_id)

    context = {
        "test": test
    }

    return render(request, 'tests/test_preview.html', context=context)



def take_test(request, test_id):
    test = get_object_or_404(Tests, id=test_id)
    questions = test.questions.all()
    current_question = request.session.get('current_question', 0)
    
    if current_question < len(questions):
        question_instance = questions[current_question]

        if request.method == 'POST':
            form = TestForm(request.POST)
            if form.is_valid():
                # Логика обработки ответа на вопрос
                request.session['current_question'] = current_question + 1
                return redirect('tests:take_test', test_id=test.id)
        else:
            form = TestForm()
        
        return render(request, 'tests/question.html', {'form': form, 'question': question_instance, 'test': test})
    else:
        # Очистка сессии и сброс `current_question`
        request.session['current_question'] = 0
        return redirect('tests:test_results', test_id=test.id)


    

def test_results(request, test_id):
    return render(request, 'tests/test_results.html')