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
def test_home_page(client):
    test_logger.info('Start test_home_page')
    user = pytest.test_user
    test_logger.info(f"USER  {user}")
    login = client.login(username='testuser', password="testpass123")
    assert login
    
    # test_data=  test_page_data(
    #     all_tests=10,
    #     test_results=True,
    #     random_data=True

    # )
    response = client.get(reverse('app:index'))

    assert response.status_code == 200
    
    test_logger.info(f"{response.context['group_data']}") 