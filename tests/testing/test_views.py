from unicodedata import category
from urllib import response
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from django.urls import reverse, reverse_lazy
from django.utils import timezone
import pytest
import test
from conftests import (
    test_page_data, 
    global_config, 
    test_user, 
    users_data, 
    get_test_result,
    create_one_test,
    form_data_from_test,
    question_combination,
    create_one_question,
    answers_form_data,
    matching_pairs_form_data
)
import logging

from tests.models import Categories, Question, QuestionGroup, TestResult, Tests
from users.models import Group, User

test_logger = logging.getLogger('test_logger')

@pytest.mark.run(order=1)
def test_000_created_data(test_page_data):
    """Создает тестовые данные с нужными параметрами"""
    result = test_page_data()


# Тестирование домашней страницы

@pytest.mark.run(order=2)
@pytest.mark.django_db
def test_home_page_no_authenticate_user(client):
    test_logger.info('Start test_home_page')
    # login = client.login(username='testuser', password="testpass123")
    # assert login
    
    response = client.get(reverse('app:index'))
    assert response.status_code == 302
    
    
@pytest.mark.run(order=3)
@pytest.mark.django_db
def test_home_page_authenticate_user(client, global_config, users_data):
    super_user = users_data.get('testsuperuser', None)
    assert super_user

    login = client.login(username=super_user['username'], password=super_user['password'])
    assert login

    response = client.get(reverse('app:index'))
    test_logger.info(f"{[t.name for t in response.templates]}")
    assert response.status_code == 200
    group_data = response.context['group_data'].get('Group 0', None)
    assert 'app/index.html' in [t.name for t in response.templates]
    assert group_data

    test_logger.info(f"response_context - {group_data}")
    assert group_data['group_name'] == 'testGroup'

    all_tests_len = global_config.all_tests

    # Расчитываем количество тестов для резульатата тестов и тестов на проверку (Приоритет у test_reviews при нечётном количестве тестов)
    if global_config.test_results or global_config.test_reviews:
        result_len = round(global_config.all_tests / 2)
        test_reviews = global_config.all_tests - result_len
        test_results = global_config.all_tests - test_reviews


    if global_config.test_results:
        all_tests_len = all_tests_len - test_results
        assert len(group_data['test_results']) == test_results
        
    if global_config.test_reviews:
        all_tests_len = all_tests_len - test_reviews
        assert len(group_data['test_reviews']) == test_reviews

    test_logger.info(f"LEN {all_tests_len}")
    assert len(group_data['uncomplete_tests']) == all_tests_len


# Тестирование страницы рейтинга

@pytest.mark.run(order=3)
@pytest.mark.django_db
def test_rating_page_special_user(client, global_config, users_data):
    # Проверяем что без логина пользователь будет перенаправлен на страницу логина
    response = client.get(reverse('tests:rating'))
    assert response.status_code == 302

    super_user = users_data.get('testsuperuser', None)
    assert super_user

    login = client.login(username=super_user['username'], password=super_user['password'])
    assert login
    
    response = client.get(reverse('tests:rating'))
    assert response.status_code == 200
    assert 'tests/rating.html' in [t.name for t in response.templates]
    
    group_data = response.context['groups'].get('Group 0', None)

    assert group_data
    assert group_data['group_name'] == 'testGroup'

    test_logger.info(f"{group_data}")
    assert len(group_data['tests']) == global_config.all_tests


@pytest.mark.run(order=4)
@pytest.mark.django_db
def test_rating_page_user(client, global_config, users_data):

    user = users_data.get('testuser', None)
    assert user

    login = client.login(username=user['username'], password=user['password'])
    assert login

    response = client.get(reverse('tests:rating'))

    assert response.status_code == 200
    
    # test_logger.info(f"{response.context}")
    group_data = response.context['groups'].get('Group 0', None)

    assert group_data
    
    if global_config.test_results:
        test_result_len = global_config.all_tests // 2
        test_logger.info(f"{test_result_len}")
        assert len(group_data['tests']) == test_result_len
    else:
        assert len(group_data['tests']) == 0

    test_logger.info(f"{group_data}")


@pytest.mark.run(order=4)
@pytest.mark.django_db
def test_rating_test_page(client, global_config, users_data, get_test_result):
    test = get_test_result

    if global_config.test_results:
        assert test

        response = client.get(reverse('tests:rating_test', kwargs={"test_id": test.id}))
        assert response.status_code == 302

        superuser = users_data['testsuperuser']
        login = client.login(username=superuser['username'], password=superuser['password'])
        assert login

        response = client.get(reverse('tests:rating_test', kwargs={"test_id": test.id}))
        assert response.status_code == 200

        test_logger.info(f"{response.context['results']}")
        assert len(response.context['results']) == 1
        assert response.context['test_name'] == test.name

    test_logger.info(f"{get_test_result}")


# Проверка главной странички для учителей
@pytest.mark.run(order=5)
@pytest.mark.django_db
def test_all_tests_page_user(client, users_data):
    user = users_data['testuser']
    assert user
    login = client.login(username=user['username'], password=user['password'])
    assert login

    response = client.get(reverse('tests:all_tests'))
    assert response.status_code == 403


@pytest.mark.run(order=6)
@pytest.mark.django_db
def test_all_tests_page_superuser(client, users_data, global_config):
    superuser = users_data['testsuperuser']
    assert superuser
    login = client.login(username=superuser['username'], password=superuser['password'])
    assert login 

    response = client.get(reverse('tests:all_tests'))
    assert response.status_code == 200
    assert len(response.context['tests']) == global_config.all_tests
    assert "tests/all_tests.html" in [t.name for t in response.templates]


@pytest.mark.run(order=7)
@pytest.mark.django_db
def test_all_tests_page_teacher(client, users_data, create_one_test):
    teacher = users_data['testteacher']
    login = client.login(username=teacher['username'], password=teacher['password'])
    assert login

    create_one_test(user=pytest.test_teacher, group=pytest.test_teacher.group.first())

    response = client.get(reverse('tests:all_tests'))
    assert response.status_code == 200

    assert len(response.context['tests']) == 1


@pytest.mark.run(order=8)
@pytest.mark.django_db
def test_all_test_page_filtration(client, users_data, global_config):
    if not global_config.random_data:
        superuser = users_data['testsuperuser']
        assert superuser
        login = client.login(username=superuser['username'], password=superuser['password'])
        assert login

        url = reverse_lazy('tests:all_tests')
        test_logger.info(f"url - {url}")


        response = client.get(url)
        assert response.status_code == 200
        page_obj = response.context['page_obj']
        # test_logger.info(f"{page_obj.paginator.count}")
        assert page_obj.paginator.count == global_config.all_tests


        test = Tests.objects.first()
        assert test
        test_logger.info(f'{test}')
        response = client.get(f"{url}?search={test.name}")
        assert response.status_code == 200
        page_obj = response.context['page_obj']
        assert page_obj.paginator.count == 1


@pytest.mark.run(order=9)
@pytest.mark.django_db
def test_all_test_page_pagination(client, users_data, global_config):
    superuser = users_data['testsuperuser']
    assert superuser
    login = client.login(username=superuser['username'], password=superuser['password'])
    assert login

    url = reverse_lazy('tests:all_tests')
    response = client.get(url)

    page_obj = response.context['page_obj']
    last_page = page_obj.paginator.num_pages

    if last_page > 1:
        response = client.get(f"{url}?page={last_page}")
        page_obj = response.context['page_obj']
        test_logger.info(f"{len(page_obj)}")
        assert page_obj.object_list


# Тесты страницы создания тестов
@pytest.mark.run(order=10)
@pytest.mark.django_db
def test_create_test_page_user(client, users_data):
    test_logger.info(f"{Categories.objects.first().id} - {Group.objects.first().id}")
    response = client.get(reverse('tests:create_test'))
    assert response.status_code == 302

    user = users_data['testuser']
    assert user
    login = client.login(username=user['username'], password=user['password'])
    assert login

    response = client.get(reverse('tests:create_test'))
    assert response.status_code == 403


@pytest.mark.run(order=11)
@pytest.mark.django_db
def test_create_test_page_valid_data(client, users_data, form_data_from_test):
    teacher = users_data['testteacher']
    assert teacher

    login = client.login(username=teacher['username'], password=teacher['password'])
    assert login

    url = reverse('tests:create_test')

    category_id = Categories.objects.first().id
    group_id = Group.objects.first().id    

    form_data = form_data_from_test(category_id, group_id)

    response = client.post(url, data=form_data)
    assert response.status_code == 302

    assert Tests.objects.filter(name='test Created').exists()


@pytest.mark.run(order=12)
@pytest.mark.django_db
def test_create_test_page_not_valid_data(client, users_data, form_data_from_test):
    teacher = users_data['testteacher']
    assert teacher

    login = client.login(username=teacher['username'], password=teacher['password'])
    assert login

    url = reverse('tests:create_test')

    form_data = form_data_from_test(not_valid=True)
    response = client.post(url, data=form_data)
    assert response.status_code == 200
    test_logger.info(f"{response.context.get('detail_errors', None)}")
    detail_errors = response.context.get('detail_errors', None)
    assert detail_errors

    assert 'name' in detail_errors
    assert 'description' in detail_errors
    assert 'category' in detail_errors
    assert 'group' in detail_errors
    assert 'raw_duration' in detail_errors


# Тесты для страницы изменения теста
@pytest.mark.run(order=13)
@pytest.mark.django_db
@pytest.mark.parametrize('user, status_code', [
    (None, 302),
    ('testuser', 403),
    ('testsuperuser', 200),
    ('testteacher', 200),
])
def test_edit_test_page_status_code(client, user,status_code, users_data, global_config):
    if global_config.all_tests > 0:
        user = users_data[user] if user != None else None
        test_logger.info(f"user -> {user}")

        if user:
            login = client.login(username=user['username'], password=user['password'])
            assert login

        test = Tests.objects.first()
        url = reverse_lazy('tests:edit_test', kwargs={"pk": test.pk})

        response = client.get(url)

        test_logger.info(f"{response.status_code}")
        assert response.status_code == status_code



@pytest.mark.run(order=14)
@pytest.mark.django_db
@pytest.mark.parametrize('valid, status_code', [
    (True, 302),
    (False, 200),
])
def test_edit_test_page_form_check(client, valid, status_code,  users_data, global_config,form_data_from_test):
    if global_config.all_tests == 0:
        pytest.skip()

    superuser = users_data['testsuperuser']
    assert superuser
    login = client.login(username=superuser['username'], password=superuser['password'])
    assert login

    test = Tests.objects.first()
    url = reverse_lazy('tests:edit_test', kwargs={'pk': test.pk})

    if valid:
        form_data = form_data_from_test(edit_test=test)
    else:
        form_data = form_data_from_test(edit_test=test, not_valid=True)

    response = client.post(url, data=form_data)

    test_logger.info(f"{response.status_code}")
    assert response.status_code == status_code

    if status_code == 302:
        test.refresh_from_db()
        assert test.duration.total_seconds() != form_data['duration']

    

# Тесты для удаления теста
@pytest.mark.run(order=15)
@pytest.mark.django_db
@pytest.mark.parametrize('user, status_code', [
    (None, 403),
    ('testuser', 403),
    ('testteacher', 302),
    ('testsuperuser', 302),
])
def test_delete_test_view(client,user, status_code,  users_data, global_config, create_one_test):
    if global_config.all_tests == 0:
        pytest.skip()

    user = users_data[user] if user != None else None
    if user:
        login = client.login(username=user['username'], password=user['password'])
        assert login

    if user:
        test_logger.info(f"{user}")

        if user['username'] == 'testuser':
            model_user = User.objects.get(username=pytest.test_superuser.username)
        else:
            model_user = User.objects.get(username=user['username'])

        group = model_user.group.first()

        test_logger.info(f"{model_user} - {group}")
        test = create_one_test(user=model_user, group=group)
    else:
        test = Tests.objects.first()

    
    url = reverse('tests:delete_test', kwargs={'test_id': test.id})

    response = client.post(url)
    test_logger.info(f"{response.status_code}")
    assert response.status_code == status_code
    # test.refresh_from_db()

    if status_code == 302:
        with pytest.raises(Tests.DoesNotExist):
            Tests.objects.get(pk=test.pk)
        

# Тесты для Добавления группы для вопросов в тест
@pytest.mark.run(order=16)
@pytest.mark.django_db
@pytest.mark.parametrize('user, status_code', [
    (None, 302),
    ('testuser', 403),
    ('testteacher', 200),
    ('testsuperuser', 200),
])
def test_add_question_group_response_code(client, user, status_code, users_data, global_config, create_one_test):
    if global_config.all_tests == 0:
        pytest.skip()

    user = users_data[user] if user != None else None
    if user:
        login = client.login(username=user['username'], password=user['password'])
        assert login

    if user:
        if user['username'] == 'testuser':
            model_user = User.objects.get(username=pytest.test_superuser.username)
        else:
            model_user = User.objects.get(username=user['username'])

        group = model_user.group.first()

        test = create_one_test(model_user, group)
    else:
        test = Tests.objects.first()


    url = reverse('tests:add_question_group', kwargs={'test_id': test.id})
    response = client.get(url)
    assert response.status_code == status_code


@pytest.mark.run(order=17)
@pytest.mark.django_db
@pytest.mark.parametrize('user, question_group_name, status_code', [
    ('testsuperuser','test question group', 302),
    ('testsuperuser','', 200),
    ('testteacher','test question group', 302),
    ('testteacher','', 200),
])
def test_add_question_group_created_from_teacher(client,user, question_group_name, status_code, users_data, create_one_test, global_config):
    if global_config.all_tests == 0:
        pytest.skip()

    user = users_data[user]

    login = client.login(username=user['username'], password=user['password'])
    assert login
    user_model = User.objects.get(username=user['username'])
    group = user_model.group.first()
    
    test = create_one_test(user_model, group)
    url = reverse('tests:add_question_group', kwargs={'test_id': test.id})

    form_data = {'name': question_group_name}

    response = client.post(url, data=form_data)
    assert response.status_code == status_code

    if status_code == 302:
        assert QuestionGroup.objects.filter(name=question_group_name).exists()


# Тесты странци создания вопросов и добавления студентов

@pytest.mark.run(order=18)
@pytest.mark.django_db
@pytest.mark.parametrize('username, status_code', [
    (None, 302),
    ('testuser', 403),
    ('testteacher', 200),
    ('testsuperuser', 200),
])
def test_create_question_response_code(client,username, status_code, users_data, global_config):
    if global_config.all_tests == 0:
        pytest.skip()

    test = Tests.objects.first()
    user = users_data[username] if username else None

    if user:
        login = client.login(username=user['username'], password=user['password'])
        assert login

    url = reverse('tests:add_questions', kwargs={'test_id': test.id})

    response = client.get(url)

    assert response.status_code == status_code
    

@pytest.mark.run(order=19)
def test_create_question_full_variants(client,users_data, question_combination):
    # test_logger.info(question_combination)
    superuser = users_data['testsuperuser']
    login = client.login(username=superuser['username'], password=superuser['password'])
    assert login
    test_id = question_combination['test']

    url = reverse('tests:add_questions', kwargs={'test_id': test_id})

    response = client.post(url, data=question_combination)
    if response.context and response.context.get('errors', None):
        test_logger.info(response.context['errors'])
    assert response.status_code == 302
    test = Tests.objects.get(id=test_id)

    assert len(test.questions.all()) == 1


@pytest.mark.run(order=20)
@pytest.mark.django_db
@pytest.mark.parametrize('users, users_count, form_valid', [
    (3, 3, True,),
    (2, 2, True,),
    (0, 0, True),
    (0, 1, False), # superuser default user in all  test.students.all()
])
def test_create_questions_page_test_adding_students(client, users, users_count, form_valid, users_data, global_config):
    if global_config.all_tests == 0:
        pytest.skip()

    user = users_data['testsuperuser']
    login = client.login(username=user['username'], password=user['password'])
    assert login

    test = Tests.objects.first()
    test_logger.info(f"STUDENTS {test.students.all()}")

    if users != 0:
        users_set = set(User.objects.all().values_list('id', flat=True)[:users])
    else:
        users_set = set()

    if form_valid:
        form_data = {
            'form_type': 'form_student',
            'students': users_set,
        }
    else:
        form_data = {
            'form_type': 'form_student',
            'students': 'bobfsdfsd'
        }

    url = reverse('tests:add_questions', kwargs={'test_id': test.id})

    response = client.post(url, data=form_data)
    assert response.status_code == 202 if form_valid else 404

    test_logger.info(f"{test.students.all()}")
    assert test.students.all().count() == users_count

    test_logger.info(f"{users_set}")


@pytest.mark.run(order=21)
@pytest.mark.django_db
@pytest.mark.parametrize('user_name, status_code', [
    (None, 302),
    ('testuser', 403),
    ('testteacher', 302),
    ('testsuperuser', 302),
])
def test_delete_question(client,user_name ,status_code, users_data , create_one_question, global_config):
    if global_config.all_tests == 0:
        pytest.skip()
    
    test = Tests.objects.first()
    question = create_one_question(test)

    user = users_data[user_name] if user_name else None

    if user:
        login = client.login(username=user['username'], password=user['password'])
        assert login

    url = reverse('tests:delete_question', kwargs={'question_id': question.id})

    response = client.post(url)

    assert response.status_code == status_code

    if user in ['testteacher', 'testsuperuser'] and status_code == 302:
        with pytest.raises(Question.DoesNotExist):
            question.refresh_from_db()

# Тесты для страниц добавления вопроса
@pytest.mark.run(order=22)
@pytest.mark.django_db
def test_add_answers_page_add_answer(client, users_data,answers_form_data):
    user = users_data['testsuperuser']
    assert user
    login = client.login(username=user['username'], password=user['password'])
    assert login

    form_data, question = answers_form_data
    valid_form = form_data['valid']

    del form_data['valid']

    url = reverse('tests:add_answers', kwargs={'question_id': question.id})

    # test_logger.info(form_data)
    response = client.post(url, data=form_data)
    # test_logger.info(response.status_code)

    assert response.status_code == 302 if valid_form else 200

    if response.status_code == 200:
        assert 'score' in [ error for error in response.context['form'].errors]
        # assert response.context['form']


@pytest.mark.run(order=23)
@pytest.mark.django_db
def test_add_matching_pairs_page_create(client,users_data, matching_pairs_form_data):
    user = users_data['testsuperuser']
    assert user

    login = client.login(username=user['username'], password=user['password'])
    assert login

    form_data, question = matching_pairs_form_data
    valid_form = form_data['valid']

    question_found = Question.objects.filter(id=question.id).exists()
    assert question_found
    test_logger.info(question_found)

    del form_data['valid']

    url = reverse('tests:add_matching_pair', kwargs={'question_id': question.id})

    test_logger.info(f"{url} - {form_data}")
    response = client.post(url, data=form_data)
    test_logger.info(response)
    assert response.status_code == 302 if valid_form else 200
