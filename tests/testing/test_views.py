from django.urls import reverse
import pytest
import test
from conftests import test_page_data, global_config
import logging

test_logger = logging.getLogger('test_logger')

@pytest.mark.run(order=1)
def test_000_created_data(test_page_data, global_config):
    """Создает тестовые данные с нужными параметрами"""
    test_logger.info(f"TEST CONFIG {global_config}")
    result = test_page_data()

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
def test_home_page_authenticate_user(client, global_config):
    login = client.login(username='testuser', password="testpass123")
    assert login

    response = client.get(reverse('app:index'))
    assert response.status_code == 200
    test_logger.info(f"{response.context['group_data']}")

    group_data = response.context['group_data']['Group 0']

    test_logger.info(f"response_context - {group_data}")

    assert group_data['group_name'] == 'testGroup'

    result_len = round(global_config.all_tests / 2)

    test_reviews = global_config.all_tests - result_len

    test_results = global_config.all_tests - test_reviews

    test_logger.info(f'LEN {test_reviews}')
    test_logger.info(f'LEN {test_results}')

    if global_config.test_results:
        assert len(group_data['test_results']) == test_results
    
    if global_config.test_reviews:
        assert len(group_data['test_reviews']) == test_reviews