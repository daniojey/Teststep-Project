from urllib import response
from django.urls import reverse
import pytest
import test
from conftests import test_page_data, global_config, test_user, users_data, get_test_result
import logging

from tests.models import TestResult

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