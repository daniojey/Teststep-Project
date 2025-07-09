from datetime import datetime
from enum import member
import logging
from os import name
from unicodedata import category
from wsgiref.util import request_uri

from django.utils import duration
from django.utils import timezone
from django.utils.timezone import make_aware, timedelta
from tests.admin import date_in, date_out
from tests.models import Categories, TestResult, Tests
import pytest
from random import choice, randint, choices

from tests.testing.utils.view_utils import create_test_results, create_tests, create_test_reviews, create_category
from users.models import Group, User
from config import СURRENT_CONFIG

test_logger = logging.getLogger('test_logger')

@pytest.fixture
def users_data():
    """Для получения данных пользователя в тестах для логина"""
    return {
        'testuser': {
            'username': 'testuser',
            'password': 'testpass123',
        },
        'testsuperuser': {
            'username': 'testsuperuser',
            'password': 'testpass123',
        },
        'testteacher': {
            'username': 'testteacher',
            'password': 'testpass123',
        }
    }

@pytest.fixture(scope='session')
def global_config():
    """
    Глобальный конфиг для всех тестов
    """
    test_logger.info(f'Инициализация конфига {СURRENT_CONFIG}')
    return СURRENT_CONFIG

@pytest.fixture
def test_super_user(db):
    """ Фикстура для создания кастомного пользователя"""
    return User.objects.create_superuser(
        username="testsuperuser",
        email="2@gmail.com",
        password="testpass123",
        teacher=True,
    )

@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="testuser",
        email="5@gmail.com",
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

            user = User.objects.create_superuser(
                username="testsuperuser",
                email="1@gmail.com",
                password="testpass123",
                teacher=True,
            )

            student = User.objects.create_user(
                username="testuser",
                email="3@gmail.com",
                password="testpass123",
            )

            teacher = User.objects.create_user(
                username='testteacher',
                email="4@gmail.com",
                password='testpass123',
                is_staff=True,
                teacher=True,
            )
            
            pytest.test_superuser = user
            pytest.test_student = student
            pytest.test_teacher = teacher

            group = Group.objects.create(
                name="testGroup",
            )

            group.members.set((user.id, student.id, teacher.id))

            test_logger.info(f'MEMBERS {group.members.all()}')

            category = create_category(random_data=random_data)

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

            return '1'

    return _test_page_data
        

    
@pytest.fixture
def get_test_result():
    result = TestResult.objects.all().first()
    
    if result:
        return result.test
    else:
        return None


@pytest.fixture
def create_one_test(db):
    def _create_one_test(user, group):
        test = Tests.objects.create(
            user=user,
            group=group,
            name=f"TEST {user.username}",
            description=f"test desc",
            duration = timedelta(minutes=30),
            date_in=timezone.now(),
            date_out=timezone.now() + timedelta(weeks=2),
            category=Categories.objects.first(),
            check_type=choices(["auto","manual"]),
        )

        test_logger.info(f"{test}")

        return test

    return _create_one_test


@pytest.fixture
def form_data_from_test(db):
    def _construct_data(category_id=None, group_id=None, not_valid=False) -> dict:
        
        if not_valid:
            data = {
                'name': 'test 0',
                'description': 'a' * 501,
                # 'category': category_id,
                'check_type': 'auto',
                'raw_duration': '100xв',
                # 'group': group_id,
                'date_in': timezone.now(),
                'date_out': timezone.now() + timezone.timedelta(weeks=2)
            }

        else:

            data = {
                'name': 'test Created',
                'description': 'test desc',
                'category': category_id,
                'check_type': 'auto',
                'raw_duration': 60,
                'group': group_id,
                'date_in': timezone.now(),
                'date_out': timezone.now() + timezone.timedelta(weeks=2)
            }

        return data
    return _construct_data





        