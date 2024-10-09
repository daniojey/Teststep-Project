# tests/views.py
import random
from traceback import print_tb
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from tests.strategy import MultypleChoiceStrategy
from users.models import User, UsersGroupMembership
from .models import MatchingPair, QuestionGroup, TestResult, Tests, Question, Answer, TestsReviews
from .forms import MatchingPairForm, QuestionGroupForm, QuestionStudentsForm, TestForm, QuestionForm, AnswerForm, TestReviewForm, TestTakeForm
from django.core.files.base import ContentFile
import base64
import os
from django.core.files.storage import default_storage

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
        # Если у пользователя нет группы
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
            # Сначала создаем тест, но не сохраняем его в базе
            test = form.save(commit=False)  
            test.user = request.user  # Присваиваем пользователя

            # Получаем список ID студентов
            selected_students = form.cleaned_data.get('students')
            
            # Сохраняем студентов в поле JSON в формате [1, 2, 3]
            test.students = {'students': selected_students}
            
            # Сохраняем тест
            test.save()

            # Далее можно перенаправить на другую страницу
            return redirect('tests:add_questions', test_id=test.id)
    else:
        form = TestForm(user=request.user)
    
    return render(request, 'tests/create_test.html', {'form': form})


def delete_test(request, test_id):
    test = get_object_or_404(Tests, id=test_id)
    test.delete()
    return redirect('app:index')


@login_required
def add_question_group(request, test_id):
    test = get_object_or_404(Tests, pk=test_id)

    if request.method == 'POST':
        form = QuestionGroupForm(request.POST)
        if form.is_valid():
            question_group = form.save(commit=False)
            question_group.test = test
            question_group.save()
            return redirect("tests:add_questions",  test_id=test.id)

    else:
        form = QuestionGroupForm()


    context = dict(form=form)

    return render(request, 'tests/adq.html', context=context)


@login_required
def add_questions(request, test_id):
    user = get_object_or_404(User, id=request.user.id)
    test = get_object_or_404(Tests, pk=test_id)
    question_groups = QuestionGroup.objects.filter(test=test).prefetch_related('questions_group')
    ungrouped_questions = Question.objects.filter(test=test, group__isnull=True)

    # POST-запрос: Обрабатываем форму в зависимости от переданного form_type
    if request.method == 'POST':
        form_type = request.POST.get('form_type')  # Определяем тип формы

        # Обработка формы вопросов
        question_form = QuestionForm(request.POST, request.FILES, test=test)

        # Обработка формы студентов
        student_form = QuestionStudentsForm(request.POST, request.FILES, test=test, user=user)

        if form_type == 'form_question':
            if question_form.is_valid():
                question = question_form.save(commit=False)
                question.test = test  # Привязываем вопрос к текущему тесту
                question.save()
                return redirect('tests:add_questions', test_id=test.id)

        elif form_type == 'form_student':
            if student_form.is_valid():
                test.students = {'students': student_form.cleaned_data.get('students')}
                test.save()
                return redirect('tests:add_questions', test_id=test.id)
            else:
                print(student_form.errors)
                return redirect('tests:add_questions', test_id=test.id)

    else:
        question_form = QuestionForm(test=test)
        student_form = QuestionStudentsForm(test=test, user=user)    

    # Запросы для отображения данных
    questions = Question.objects.filter(test=test)

    # Контекст для шаблона
    context = {
        'test': test,
        'question_form': question_form,  
        'questions': questions,  # Список всех вопросов
        'question_groups': question_groups,  # Группированные вопросы
        'ungrouped_questions': ungrouped_questions,  # Негруппированные вопросы
        'form_student': student_form  # Форма для выбора студентов
    }

    return render(request, 'tests/add_questions.html', context=context)


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
        'form': answer_form,
        'form_type':'Ответ',
        'action_url':'tests:add_answers',
    })

def add_matching_pair(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    test = question.test
    questions = test.questions.all()


    if request.method == "POST":
        matching_pair_form = MatchingPairForm(request.POST)
        if matching_pair_form.is_valid():
            answer = matching_pair_form.save(commit=False)
            answer.question = question
            answer.save()
            return redirect('tests:add_matching_pair', question_id=question.id)
    else:
        matching_pair_form = MatchingPairForm()
    return render(request, 'tests/add_answer.html', {
        'test': test,
        'question': question,
        'questions': questions,
        'form': matching_pair_form,
        "form_type":"Соотвецтвие",
        "action_url":'tests:add_matching_pair',
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
    
    # Если тест только начался, инициализируем сессию для теста
    if 'question_order' not in request.session:
        # Получаем вопросы, отсортированные по группам
        questions_by_group = {}
        for group in QuestionGroup.objects.filter(test=test):
            questions_by_group[group.name] = list(group.questions_group.all())


        # Перемешиваем вопросы внутри каждой группы
        for group_name, questions in questions_by_group.items():
            random.shuffle(questions)  # Перемешиваем вопросы в группе

        # Объединяем все перемешанные вопросы в один список
        all_questions = []
        for group_name, questions in questions_by_group.items():
            all_questions.extend(questions)

        #Для вопросов без группы
        questions_not_group = {}
        # for group in Question.objects.filter(test=test, group=None):
        questions_not_group['All'] = list(Question.objects.filter(test=test, group=None))
        print(questions_not_group)

        # Перемешиваем вопросы и добавляем их к остальным
        for _ , questions in questions_not_group.items():
            random.shuffle(questions)
            all_questions.extend(questions)


    
        # Сохраняем порядок вопросов в сессии
        request.session['question_order'] = [q.id for q in all_questions]
        request.session['question_index'] = 0  # Начинаем с первого вопроса
        request.session['test_responses'] = {}  # Для хранения ответов пользователя
        
    question_order = request.session['question_order']
    question_index = request.session['question_index']
    
    # Проверяем, не завершен ли тест (когда все вопросы пройдены)
    if question_index >= len(question_order):
        if test.check_type == 'manual':
            return redirect('tests:success_page')
        else:
            return redirect('tests:test_results', test_id=test_id)
    
    # Текущий вопрос
    current_question_id = question_order[question_index]
    current_question = get_object_or_404(Question, id=current_question_id)
    # current_question_group = QuestionGroup.objects.filter(question=current_question).first()

    try:
        current_question_group = current_question.group.name
    except:
        current_question_group = 'Усі'
    
    # Форма для текущего вопроса
    if request.method == 'POST':
        form = TestTakeForm(request.POST, question=current_question)
        if form.is_valid():
            # Обрабатываем разные типы вопросов
            if current_question.question_type == 'AUD':
                # Для аудиовопросов используем 'audio_answer'
                answer = form.cleaned_data.get(f'audio_answer_{current_question_id}', None)
            else:
                # Для всех остальных вопросов используем 'answer'
                answer = form.cleaned_data.get('answer', None)

            if current_question.question_type == 'AUD':
                # Сохраняем в сессии с префиксом 'audio_answer_'
                if answer is not None:
                    request.session['test_responses'][f"audio_answer_{current_question_id}"] = answer
            elif current_question.question_type == 'MTCH':
                responses = request.POST


                dict_items = {}
                for left, right in responses.items():
                   if left.startswith('answer_'):  # Проверяем, что это поле с ответом
                        left_item = left.split('answer_')[1]  # Получаем левый элемент
                        dict_items[left_item] = right
                
                request.session['test_responses'][f'question_{current_question_id}_type_matching'] = dict_items


            else:
                # Для всех остальных типов вопросов используем 'question_{id}'
                if answer is not None:
                    request.session['test_responses'][f"question_{current_question_id}"] = answer
                            
            # Переход к следующему вопросу
            request.session['question_index'] += 1

            return redirect('tests:take_test', test_id=test_id)  # Перезагрузка на следующий вопрос
    else:
        form = TestTakeForm(question=current_question)

    # Статистика по вопросам
    all_questions = {
        "current": question_index + 1,
        "all": len(question_order)
    }

    return render(request, 'tests/question.html', {
        'form': form,
        'test': test,
        'question': current_question,
        'all_questions': all_questions,
        'current_question_group': current_question_group,
    })


def test_results(request, test_id):
    test = get_object_or_404(Tests, id=test_id)
    responses = request.session.get('test_responses', {})
    audio_answers = request.session.get('audio_answer_', {})


    if test.check_type == Tests.MANUAL_CHECK:
            for key, value in responses.items():
                if 'audio_answer_' in key and value:
                    # Преобразуем base64 в файл
                    question_id = key.split('audio_answer_')[1]
                    audio_data = value.split(',')[1]  # Убираем префикс base64
                    audio_content = base64.b64decode(audio_data)
                    
                    # Генерируем имя файла
                    filename = f"audio_answer_{question_id}_{request.user.id}.webm"
                    file_path = os.path.join('answers/audios/', filename)
                    audio_file = ContentFile(audio_content, filename)
                    
                    # Сохраняем файл в систему
                    saved_file = default_storage.save(file_path, audio_file)
                    
                    # Получаем URL файла
                    file_url = default_storage.url(saved_file)
                    
                    # Сохраняем URL аудиофайла по вопросу в словаре
                    audio_answers[question_id] = file_url

            request.session['audio_answers'] = audio_answers


    if test.check_type == Tests.MANUAL_CHECK:
        review = TestsReviews.objects.create(
            test=test,
            user=request.user,
            answers=responses,
            audio_answers=audio_answers,  # Сохраняем аудио-ответы для ручной проверки
                # group=request.user.profile.group,  # Если у пользователя есть группа
        )

        if 'question_order' in request.session:
            del request.session['question_order']
        if 'question_index' in request.session:
            del request.session['question_index']
        if 'test_responses' in request.session:
            del request.session['test_responses']

        return render(request, 'app/success_page_manual_test.html')
    

    total_questions = test.questions.count()
    correct_answers = 0.0


    for key, value in responses.items():
        if key.startswith('question_'):
            question_id = int(key.split('_')[1])
            question = Question.objects.get(id=question_id)
            
            if question.question_type == 'SC':
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and correct_answer.id == int(value):
                    correct_answers += 1.0
            elif question.question_type == 'MC':
                correct_answers_list = question.answers.filter(is_correct=True).values_list('id', flat=True)
                if set(map(int, value)) == set(correct_answers_list):
                    correct_answers += 1.0
            elif question.question_type == 'IMG':
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and correct_answer.id == int(value):
                    correct_answers += 1.0
            elif question.question_type == 'AUD':
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and correct_answer.id == int(value):
                    correct_answers += 1.0
            elif question.question_type == "INP":
                correct_answer = question.answers.filter(is_correct=True).first()
                if str(correct_answer).strip().lower() == str(value).strip().lower():
                    correct_answers += 1.0
            elif question.question_type == 'MTCH':
                questions_count = MatchingPair.objects.filter(question=question).count()
                points = 1 / questions_count
                
                for left, right in value.items():
                    if MatchingPair.objects.filter(question=question, left_item=left, right_item=right).exists():
                        correct_answers += points 


    score = (correct_answers / total_questions) * 100
    score = round(score)

    if request.user.is_authenticated:
        test_result, created = TestResult.objects.get_or_create(
            user=request.user,
            test=test,
            defaults={'score': score, 'attempts': 1}
        )
        
        if not created:
            if test_result.remaining_atemps > 0:
                test_result.attempts += 1
                test_result.score = max(test_result.score, score)  # Сохраняем лучший результат
                test_result.save()
            else:
                return render(request, 'users/profile.html')
            
    if 'question_order' in request.session:
        del request.session['question_order']
    if 'question_index' in request.session:
        del request.session['question_index']
    if 'test_responses' in request.session:
        del request.session['test_responses']

    correct_answers = int(correct_answers)
            
    context = {
        'test': test,
        'score': score,
        'correct_answers': correct_answers,
        'total_questions': total_questions
    }
    
    return render(request, 'tests/test_results.html', context)

def success_manual_test(request):
    return render(request, 'tests/success_page_manual_test.html')


def tests_for_review(request):
    user = get_object_or_404(User, id=request.user.id)
    user_groups = UsersGroupMembership.objects.filter(user=user)

    # Проверяем в какой группе находиться пользоваетель
    if user_groups.exists():
        group = user_groups.first().group
        group_memberships = UsersGroupMembership.objects.filter(group=group)
    
    
    tests_reviews = []
    for item in group_memberships:
        test = Tests.objects.filter(user=item.user, check_type='manual')
        if test:
            tests_reviews.append(test)

    tests_results = []
    for t in tests_reviews:
        for ti in t:
            if ti:
                tests_results.append(ti)

    context = {
        "test_result": tests_results,
    }


    return render(request, 'tests/tr.html', context=context)


def test_group_reviews(request, test_id):
    test = get_object_or_404(Tests, id=test_id)
    user = get_object_or_404(User, id=request.user.id)

    user_groups = UsersGroupMembership.objects.filter(user=user)

    if user_groups.exists():
        group = user_groups.first().group
        group_memberships = UsersGroupMembership.objects.filter(group=group)
        group_name = group.name
    else:
        group = None
        group_memberships = None
        group_name = "Вы не присоединились к группе"

    user_complitely_test = []
    user_reviews = []
    user_not_reviews = []
    for us in group_memberships:
        review = TestsReviews.objects.filter(user=us.user, test=test)
        results = TestResult.objects.filter(user=us.user, test=test)
        if review:    
            user_reviews.append(review)
        elif results:
            user_complitely_test.append(results)
        else:
            user_not_reviews.append(us.user)


    context = {
        'user_reviews': user_reviews,
        'user_not_reviews': user_not_reviews,
        'user_complete_test': user_complitely_test,
    }


    return render(request, 'tests/test_group_reviews.html', context=context)


def take_test_review(request, user_id, test_id):
    user = get_object_or_404(User, id=user_id)
    test = get_object_or_404(Tests, id=test_id)
    review = get_object_or_404(TestsReviews, user=user, test=test)
    answers = review.answers
    print(answers)
    audio_answers = review.audio_answers or {}


    if request.method == 'POST':
        form = TestReviewForm(test=test, answers=answers, data=request.POST)
        if form.is_valid():
            correct_answers = 0.0
            total_questions = len(test.questions.all())

            for question in test.questions.all():
                if question.question_type == 'MC':
                    
                    # Получаем правильные ответы
                    correct_answer = question.answers.filter(is_correct=True)
                    
                    corrects = [i for i in correct_answer]

                    # Получаем выбранные ответы учителем
                    selected_answer = form.cleaned_data.get(f'question_{question.id}_approve')
                    selected_unpack = [int(i) for i in selected_answer]
                    

                    # TODO Реализовать стратегию позже 
                    # multiple_choice_strategy = MultypleChoiceStrategy()
                    # multiple_choice_strategy.calculate_point(question, selected_answer, correct_answer, form)


                    if form.cleaned_data.get(f'question_{question.id}_approve'):
                        # Если правильных ответов в вопросе несколько 
                        if len(corrects) > 1:
                            points = 1 / len(corrects)
                            for i in corrects:
                                
                                item = Answer.objects.filter(id=i.id).first()
                                if item.id in selected_unpack:
                                    correct_answers += points

                        # Если один правильный ответ
                        elif len(corrects) == 1:
                            for i in corrects:
                                
                                item = Answer.objects.filter(id=i.id).first()
                                if item.id in selected_unpack:
                                    correct_answers += 1

                elif question.question_type == "SC":
                    correct_answer = question.answers.filter(is_correct=True).first()

                    try:
                        selected_answer = int(form.cleaned_data.get(f'question_{question.id}_approve')[0])
                    except (IndexError, TypeError):
                        selected_answer = None  # Если пользователь не выбрал ответ

                    # Сравниваем ответ пользователя с правильным ответом
                    if correct_answer and correct_answer.id == selected_answer:
                        correct_answers += 1

                elif  question.question_type == "IMG":
                    ...
                elif question.question_type == 'AUD':
                    audio_response = form.cleaned_data.get(f'audio_answer_{question.id}_correct')

                    if audio_response == True:
                        correct_answers += 1                   
                
                elif question.question_type == 'INP':
                    correct_answer = question.answers.filter(is_correct=True).first()


                    selected_answer = form.cleaned_data.get(f'question_{question.id}_correct')

                    if selected_answer == True:
                        correct_answers += 1

            review.audio_answers = audio_answers
            review.save()

            # TODO Переделать этот калл

            # # Сохранение результата
            score = correct_answers / total_questions * 100
            print(f"Балл по тесту: {int(score)}%")

            # # Создание TestResults и удаление TestReviews
            TestResult.objects.create(user=review.user, test=review.test, score=score, attempts=2)
            review.delete()
            return redirect('users:profile')

    else:
        form = TestReviewForm(test=test, answers=answers, audio_answers=audio_answers)

    return render(request, 'tests/take_test_review.html', {'form': form, 'review': review, 'test': test, 'audio_answers': audio_answers})