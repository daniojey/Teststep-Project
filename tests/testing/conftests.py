from datetime import datetime
from enum import member
import logging
from os import name
from wsgiref.util import request_uri

from django.utils import duration
from django.utils.timezone import make_aware, timedelta
from tests.admin import date_in, date_out
from tests.models import Categories, Tests
import pytest
from random import choice, randint, choices

from tests.testing.utils.view_utils import create_test_results, create_tests, create_test_reviews
from users.models import Group, User
from config import СURRENT_CONFIG

test_logger = logging.getLogger('test_logger')

@pytest.fixture(scope='session')
def global_config():
    """
    Глобальный конфиг для всех тестов
    """
    test_logger.info(f'Инициализация конфига {СURRENT_CONFIG}')
    return СURRENT_CONFIG

@pytest.fixture
def test_user(db):
    """ Фикстура для создания кастомного пользователя"""
    return User.objects.create_user(
        username="testuser",
        email="1@gmail.com",
        password="testpass123",
    )


@pytest.fixture(scope='session')
def test_page_data(django_db_setup, django_db_blocker, global_config):
    def _test_page_data():

        with django_db_blocker.unblock():
            all_tests = global_config.all_tests
            test_reviews = global_config.test_reviews
            test_results = global_config.test_results
            random_data = global_config.random_data
            
            test_logger.info(f'Инициализация конфига в ДАТЕ {global_config}')


            user = User.objects.create_user(
                username="testuser",
                email="1@gmail.com",
                password="testpass123",
            )

            pytest.test_user = user

            group = Group.objects.create(
                name="testGroup",
            )

            group.members.add(user)

            test_logger.info(f'MEMBERS {group.members.all()}')

            if random_data:
                category_data = []

                for i in range(randint(2, 5)):
                    category_obj = Categories(
                        name=f"testCategory {i}",
                        slug=f"test_category_{i}",
                    )

                    category_data.append(category_obj)
                
                print(category_data)
                Categories.objects.bulk_create(category_data)

                category = Categories.objects.all()
                test_logger.info(f"Категории {category}")
            else:
                Categories.objects.create(
                    name=f"testCategory",
                    slug=f"test_category"
                )

                category = Categories.objects.all()
                test_logger.info(f"Категории {category}")


            tests = create_tests(
                categories=category, 
                count_tests=all_tests,
                user=user,
                group=group,
                random_data=random_data
            )

            # result_tests = tests.order_by("?").values_list('id', flat=True)

            if random_data:
                all_test_ids = list(tests.order_by("?").values_list('id', flat=True))
            else:
                all_test_ids = list(tests.values_list('id', flat=True))

            test_logger.info(f"All_TESTS {all_test_ids}")
            
            result_len = round(all_tests / 2)
            test_logger.info(f"REsult_len {result_len}")

            all_result_ids = all_test_ids[:result_len]
            test_logger.info(f"results_ids {all_result_ids}")

            all_reviews_ids = all_test_ids[result_len:]
            test_logger.info(f"reviews_ids {all_reviews_ids}")

            if test_results and isinstance(test_results, bool):
                test_logger.info('INIT RESULTS')

                create_test_results(
                    user=user,
                    test_count=all_result_ids,
                    group=group,
                )

            if test_reviews and isinstance(test_reviews, bool):
                test_logger.info('INIT REVIEWS')

                create_test_reviews(
                    user=user,
                    test_count=all_reviews_ids,
                    group=group,
                )

            return "123"

    return _test_page_data
        

            






        