from urllib import response
from django.contrib.auth import login
from django.urls import reverse, reverse_lazy
import pytest
import test
from conftests import (
    test_page_data, 
    global_config, 
    test_user, 
    users_data, 
    get_test_result,
    create_one_test
)
import logging

from tests.models import TestResult, Tests

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

