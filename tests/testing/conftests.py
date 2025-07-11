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
from tests.models import Answer, Categories, Question, QuestionGroup, TestResult, Tests
import pytest
from random import choice, randint, choices
from django.core.files.uploadedfile import SimpleUploadedFile

from tests.testing.utils.view_utils import create_image, create_test_results, create_tests, create_test_reviews, create_category
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
    def _construct_data(category_id=None, group_id=None, not_valid=False, edit_test=None) -> dict:
        if edit_test:
            if not_valid:
                return {
                    'name': edit_test.name,
                    'description': edit_test.description,
                    'duration': 'bob', # failed,
                    'check_type': 'auto',
                    'category': 99990,
                    'group': 99999,
                    'date_in': edit_test.date_in,
                    'date_out': edit_test.date_out
                }
            
            else:
                return {
                    'name': edit_test.name,
                    'description': edit_test.description,
                    'duration': 60,
                    'check_type': edit_test.check_type,
                    'category': edit_test.category.id,
                    'group': edit_test.group.id,
                    'date_in': edit_test.date_in,
                    'date_out': edit_test.date_out
                }


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





# @pytest.fixture
# def form_data_form_question(db):
#     def _form_data_form_question(test,valid=True, scores_for=None ,question_type=None, answer_type=None,add_question_group=True):
#         if valid:
#             if add_question_group:
#                 question_group =  QuestionGroup.objects.create(name='test question group')
#             else:
#                 question_group = None

#             data = {
#                 'form_type': 'question_form',
#                 'test': test.id,
#                 'group': question_group,
#                 'scores_for': scores_for,
#                 'text': 'Question text',
#                 'question_type': question_type,
#                 'answer_type': answer_type,
#             }


#         return data
#     return _form_data_form_question

@pytest.fixture
def create_one_question(db):
    def _create_one_question(test, question_group=None, matching=False):
        question = Question.objects.create(
            test=test,
            group=question_group if question_group else None,
            scores_for=Question.SCORE_FOR_QUESTION,
            scores=1,
            text='question text',
            question_type=Question.MATCHING if matching else Question.TEXT,
            answer_type=Question.SINGLE_CHOICE,
        )
        return question
    
    return _create_one_question


@pytest.fixture(params=[
    (score_type, q_type, a_type)
    for score_type in [Question.SCORE_FOR_ANSWER, Question.SCORE_FOR_QUESTION]
    for q_type in [Question.TEXT, Question.IMAGE, Question.AUDIO, Question.MATCHING]
    for a_type in [Question.SINGLE_CHOICE, Question.MULTIPLE_CHOICE, Question.ANSWER_INPUT, Question.ANSWER_AUDIO]
])
def question_combination(request, create_one_test):
    score_type, q_type, a_type = request.param
    test_instance = create_one_test(pytest.test_superuser, pytest.test_superuser.group.first())

    data = {
        'form_type': 'form_question',
        'test': test_instance.id,
        'scores_for': score_type,
        'scores': 1,
        'question_type': q_type,
        'answer_type': a_type,
    }

    if q_type == Question.IMAGE:
        data['image'] = create_image()

    if q_type == Question.AUDIO:
        data['audio'] = SimpleUploadedFile("test.mp3", b"binary_data", content_type="audio/mpeg")

    if q_type == Question.TEXT or q_type == Question.MATCHING:
        data['text'] = "Sample question text"

    return data


@pytest.fixture(params=[
    {
        'score': 0.0,
        'text': 'answer text',
        'is_correct': True,
        'valid': True,
    },
    {
        'score': 3.0,
        'text': 'answer text',
        'is_correct': False,
        'valid': True,
    },
    {
        'score': 10.0,
        'text': 'answer text',
        'is_correct': True,
        'valid': True,
    },
    {
        'score': -10,
        'text': 'answer text',
        'is_correct': False,
        'valid': False,
    },
    {
        'score': -5,
        'text': 'answer text',
        'is_correct': True,
        'valid': False,
    },
])
def answers_form_data(request, create_one_test, create_one_question):
    score = request.param['score']
    text = request.param['text']
    is_correct = request.param['is_correct']
    valid = request.param['valid']

    user = pytest.test_superuser
    test = create_one_test(user, user.group.first())
    question = create_one_question(test)

    # test_logger.info(f"{score} - {text} - {is_correct} - {valid}")

    data = {
        'question': question.id,
        'score': score,
        'text': text,
        'is_correct': is_correct,
        'valid': valid
    }

    return data, question


@pytest.fixture(params=[
    {
        'score': 10,
        'left_item': 'l1 item',
        'right_item': 5,
        'valid': True,
    },
    {
        'score': 10,
        'left_item': 3,
        'right_item': 'r2 item',
        'valid': False,
    },
    {
        'score': 10,
        'left_item': 'l3 item',
        'right_item': 3,
        'valid': False,
    },
    {
        'score': -10,
        'left_item': 'l3 item',
        'right_item': 'r3 item',
        'valid': False,
    },
])
def matching_pairs_form_data(request, create_one_test, create_one_question):
    user = pytest.test_superuser

    score = request.param['score']
    left_item = request.param['left_item']
    right_item = request.param['right_item']
    valid = request.param['valid']
    
    test = create_one_test(user, user.group.first())
    question = create_one_question(test, matching=True)

    data = {
        'question': question.id,
        'score': score,
        'left_item': left_item,
        'right_item': right_item,
        'valid': valid
    }

    return data, question


@pytest.fixture
def create_test_detail_data(db):
    def _create_test_detail(test, questions=1, answers_for_question=2):
        question_data = []

        for i in range(questions):
            question_obj = Question(
                test=test,
                scores_for=Question.SCORE_FOR_ANSWER,
                scores=1,
                text=f'question {i}',
                question_type=Question.TEXT,
                answer_type=Question.SINGLE_CHOICE,
            )

            question_data.append(question_obj)


        created= Question.objects.bulk_create(question_data)

        test_logger.info(created)
    
        for question in created:
            
            answers_data = []
            for i in range(answers_for_question):
                answer_obj = Answer(
                    question=question,
                    score=1,
                    text=f'answer {i}',
                    is_correct=True if i == 0 else False
                )

                answers_data.append(answer_obj)

            Answer.objects.bulk_create(answers_data)

            question.update_question_score()

        
            test_logger.info(question.answers.all())

        return created
    
    return _create_test_detail