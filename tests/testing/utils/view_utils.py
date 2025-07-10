from datetime import datetime, timedelta
import logging
from random import choice, choices, randint
from io import BytesIO
from PIL import Image

from django.db.models import QuerySet
from django.utils import duration, timezone
from django.utils.timezone import localtime, make_aware, now

from tests.models import Categories, TestResult, Tests, TestsReviews

test_logger = logging.getLogger('test_logger')

def create_category(random_data: bool) -> QuerySet:
    if random_data:
        category_data = []

        for i in range(randint(2, 5)):
            category_obj = Categories(
                name=f"testCategory {i}",
                slug=f"test_category_{i}",
            )

            category_data.append(category_obj)
                
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

    return category

def create_tests(categories, user, group, count_tests, random_data: bool):
    test_logger.info("Начинаем тест my_view")
    test_logger.info(f'Данние count-tests={count_tests} random_data={random_data}')

    if random_data:
        tests_data = []

        for i in range(count_tests):
            try:
                test_obj = Tests(
                    user=user,
                    group=group,
                    name=f"test {i}",
                    description=f"test desc {i}",
                    duration = timedelta(minutes=30),
                    date_in=timezone.now(),
                    date_out=timezone.now() + timedelta(weeks=2),
                    category=choice(categories),
                    check_type=choices(["auto","manual"]),
                )
            except Exception as e:
                print(e)
                continue

            tests_data.append(test_obj)

        Tests.objects.bulk_create(tests_data)

        created = Tests.objects.all().select_related('category')

        test_students_relations = []
        ThroughModel = Tests.students.through

        for test in created:
            test_students_relations.append(
                ThroughModel(tests_id=test.id, user_id=user.id)
            )

        ThroughModel.objects.bulk_create(test_students_relations)

        test_logger.info(f"Tests = {created}")
        test_logger.info(f"test_categories = {[test.date_in for test in created]}")
        test_logger.info(f"test_categories = {[test.date_out for test in created]}")
        test_logger.info(f"test_students = {[test.students.all() for test in created]}")
    else:
        tests_data = []

        for i in range(count_tests):
            test_obj = Tests(
                user=user,
                group=group,
                name=f"test {i}",
                description=f"test desc {i}",
                duration = timedelta(minutes=30),
                date_in=timezone.now(),
                date_out=timezone.now() + timedelta(weeks=2),
                category=categories.first(),
                check_type='auto',
            )


            tests_data.append(test_obj)

        Tests.objects.bulk_create(tests_data)
        created = Tests.objects.all().select_related('category')

        test_students_relations = []
        ThroughModel = Tests.students.through

        for test in created:
            test_students_relations.append(
                ThroughModel(tests_id=test.id, user_id=user.id)
            )

        test_logger.info(test_students_relations)
        ThroughModel.objects.bulk_create(test_students_relations)

        # tests = Tests.objects.all().select_related('category')
        test_logger.info(f"Tests = {created}")
        test_logger.info(f"test_categories = {[test.date_in for test in created]}")
        test_logger.info(f"test_categories = {[test.date_out for test in created]}")
        test_logger.info(f"test_students = {[test.students.all() for test in created]}")

    return created


def create_test_results(user, test_count, group):
    test_data = list(Tests.objects.filter(id__in=test_count))

    test_results_data = []

    for i in range(len(test_count)):
        result_obj = TestResult(
            user=user,
            test=test_data[i],
            group=group,
            score=i * 10 if i * 10 <= 100 else 100,
            duration="00:10:00"
        )

        test_results_data.append(result_obj)

    created = TestResult.objects.bulk_create(test_results_data)

    # test_results = TestResult.objects.select_related('test').filter(test__id__in=test_count)
    test_logger.info(f"TEST results data {created}")


def create_test_reviews(user, test_count, group):
    test_data = list(Tests.objects.filter(id__in=test_count))


    test_results_data = []

    for i in range(len(test_count)):
        review_obj = TestsReviews(
            test=test_data[i],
            user=user,
            duration='00:10:00',
            answers={"question_0": 'answer_0'},
            group=group
        )

        test_results_data.append(review_obj)

    created = TestsReviews.objects.bulk_create(test_results_data)
    result_ids = [item.id for item in created]

    test_reviews = TestsReviews.objects.filter(id__in=result_ids)

    test_logger.info(f"TEST_REVIEWS {test_reviews}")
    return test_reviews


def create_image():
    file = BytesIO()
    image = Image.new('RGB', (1, 1), color='red')
    image.save(file, 'jpeg')
    file.name = 'test.jpg'
    file.seek(0)
    return file