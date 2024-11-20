from ast import arg
from urllib import response
from django.contrib.auth import get_user_model
from django.db import DataError, IntegrityError, transaction
from django.test import TestCase
from datetime import date, timedelta, timezone

from django.urls import reverse
from tests.forms import AnswerForm, MatchingPairForm, QuestionGroupForm, TestForm


from tests.models import Answer, Categories, MatchingPair, Question, QuestionGroup, TestResult, Tests, TestsReviews
from users.models import UsersGroup, UsersGroupMembership

# Create your tests here.

User = get_user_model()

class TetsModelTest(TestCase):
    
    def setUp(self) -> None:
        self.user = User.objects.create(username='testuser')
        self.client.login(username='testuser')

        self.category = Categories.objects.create(name='testcategory', slug='test_category')
        
        self.test = Tests.objects.create(
            user=self.user,
            name='testname',
            description='test_description',
            category=self.category,
            check_type='auto',
            date_out=date(2021, 1, 4),
            duration=timedelta(seconds=55)
        )

    def test_test_creation(self):
        self.assertEqual(self.test.name, 'testname')
        self.assertEqual(self.test.user.username, 'testuser')
        self.assertEqual(self.test.description, 'test_description')
        self.assertEqual(self.test.category.name, 'testcategory')
        self.assertEqual(self.test.check_type, 'auto')
        self.assertEqual(self.test.date_out, date(2021, 1, 4))
        self.assertEqual(self.test.duration.total_seconds(), 55)
        self.assertEqual(type(self.test.students), list)
        
    
    def test_image_is_none(self):
        self.assertFalse(self.test.image)

    def test_test_in_unique(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Tests.objects.create(
                    user=self.user,
                    name='testname',
                    description='test_description',
                    category=self.category,
                    check_type='auto',
                    date_out=date(2021, 1, 4),
                    duration=timedelta(seconds=55)
                )
    
    def tearDown(self):
        self.user.delete()
        self.category.delete()
        self.test.delete()



class QuestionGroupModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.client.login(username='testuser')

        self.category = Categories.objects.create(name='testcategory', slug='test_category')
        
        self.test = Tests.objects.create(
            user=self.user,
            name='testname',
            description='test_description',
            category=self.category,
            check_type='auto',
            date_out=date(2021, 1, 4),
            duration=timedelta(seconds=55)
        )

        self.question_group = QuestionGroup.objects.create(name='test_questiongroup', test=self.test)

    def test_questiongroup_create(self):
        self.assertEqual(self.question_group.name, 'test_questiongroup')
        self.assertEqual(self.question_group.test, self.test)

    def test_questiongroup_name_exceeds_max_length(self):
        with transaction.atomic():
            with self.assertRaises(DataError):
                test_name = 'x' * 156

                self.question_group_2 = QuestionGroup.objects.create(
                    name=test_name,
                    test=self.test,
                )

    def test_questiongroup_str_return(self):
        self.assertEqual(self.question_group.__str__(), f"Группа - {self.question_group.name}: Тест - {self.test}")

    def tearDown(self):
        self.user.delete()
        self.test.delete()
        self.category.delete()
        self.question_group.delete()



class QuestionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.client.login(username='testuser')

        self.category = Categories.objects.create(name='testcategory', slug='test_category')
        
        self.test = Tests.objects.create(
            user=self.user,
            name='testname',
            description='test_description',
            category=self.category,
            check_type='auto',
            date_out=date(2021, 1, 4),
            duration=timedelta(seconds=55)
        )

        self.question_group = QuestionGroup.objects.create(name='test_questiongroup', test=self.test)

        self.question = Question.objects.create(
            test=self.test,
            text='Text question',
            question_type = Question.SINGLE_CHOICE,
        )

        self.question_in_group = Question.objects.create(
            test=self.test,
            text='Text question in group',
            question_type = Question.MULTIPLE_CHOICE,
            group=self.question_group
        )

    def test_create_question(self):
        # Проверяем вопрос без группы
        self.assertEqual(self.question.test, self.test)
        self.assertEqual(self.question.text, 'Text question')
        self.assertEqual(self.question.question_type, 'SC')
        
        self.assertFalse(self.question.group)
        self.assertFalse(self.question.image)
        self.assertFalse(self.question.audio)

        # Проверяем вопрос с группой
        self.assertEqual(self.question_in_group.test, self.test)
        self.assertEqual(self.question_in_group.text, 'Text question in group')
        self.assertEqual(self.question_in_group.group, self.question_group)
        self.assertEqual(self.question_in_group.question_type, "MC")


        self.assertFalse(self.question_in_group.image)
        self.assertFalse(self.question_in_group.audio)

    def test_question_str_method(self):
        self.assertEqual(str(self.question), 'Text question')
        self.assertEqual(str(self.question_in_group), 'Text question in group')

    def test_question_type_variants(self):
        question_type = [Question.TEXT, Question.IMAGE, Question.AUDIO, Question.MATCHING, Question.SINGLE_CHOICE, Question.MULTIPLE_CHOICE, Question.ANSWER_INPUT, Question.ANSWER_AUDIO]
        for q_type in question_type:
            question = Question.objects.create(
                test=self.test,
                text=f'Test question of type {q_type}',
                question_type=q_type,
            )

            self.assertEqual(question.question_type, q_type)
            question.delete()

    def test_question_group_delete_behavior(self):
        self.question_group.delete()
        self.question_in_group.refresh_from_db()
        self.assertIsNone(self.question_in_group.group)

    
    def test_question_test_deletion_behavior(self):
        self.test.delete()
        with self.assertRaises(Question.DoesNotExist):
            self.question.refresh_from_db()

    def tearDown(self) -> None:
        self.user.delete()
        self.category.delete()
        self.question_in_group.delete()

        if self.test.pk:
            self.test.delete()
        
        if self.question:
            self.question.delete()

        if self.question_group.pk:
            self.question_group.delete()



class MatchingPairModelTest(TestCase):

    def setUp(self):
        
        self.user = User.objects.create(username='testuser')
        self.client.login(username='testuser')

        self.category = Categories.objects.create(name='testcategory', slug='test_category')

        self.test = Tests.objects.create(
            user=self.user,
            name='testname',
            category=self.category,
            description='test_description',
            check_type='auto',
            date_out=date(2021, 1, 4),
            duration=timedelta(seconds=55)
        )

        self.question = Question.objects.create(
            test=self.test,
            text='Text question',
            question_type = Question.MATCHING,
        )

        self.matching = MatchingPair.objects.create(
            question=self.question,
            left_item='left_test_item',
            right_item='right_test_item',
        )


    def test_matching_creation(self):
        self.assertEqual(self.matching.question, self.question)
        self.assertEqual(self.matching.left_item, 'left_test_item')
        self.assertEqual(self.matching.right_item, 'right_test_item')

    def test_matching_max_lenght(self):
        with transaction.atomic():
            with self.assertRaises(DataError):
                right_item_max = 'r' * 256
                left_item_max = 'l' * 256

                self.matching_1 = MatchingPair.objects.create(
                    question=self.question,
                    left_item='left_test_item_1',
                    right_item=right_item_max,
                )

                self.matching_2 = MatchingPair.objects.create(
                    question=self.question,
                    left_item=left_item_max,
                    right_item='right_test_item_2'
                )


    def test_matching_str_method(self):
        self.assertEqual(self.matching.__str__(), f'{self.matching.left_item} - {self.matching.right_item}')

    def test_matching_delete_question_behavior(self):
        self.question.delete()
        with self.assertRaises(MatchingPair.DoesNotExist):
            self.matching.refresh_from_db()

    def tearDown(self) -> None:
        self.user.delete()
        self.test.delete()

        if self.question.pk:
            self.question.delete()

        if self.matching.pk:
            self.matching.delete()

    

class AnswerModelTest(TestCase):
    
    def setUp(self) -> None:
        self.user = User.objects.create(username='testuser')
        self.client.login(username='testuser')

        self.category = Categories.objects.create(name='testcategory', slug='test_category')

        self.test = Tests.objects.create(
            user=self.user,
            name='testname',
            category=self.category,
            description='test_description',
            check_type='auto',
            date_out=date(2021, 1, 4),
            duration=timedelta(seconds=55)
        )

        self.question = Question.objects.create(
            test=self.test,
            text='Text question',
            question_type = Question.MATCHING,
        )

        self.answer = Answer.objects.create(
            question=self.question,
            text='text_answer',
        )

        self.answer_correct = Answer.objects.create(
            question=self.question,
            text='text_answer_is_correct',
            is_correct=True
        )
    
    def test_answer_create(self):

        # 1 ответ
        self.assertEqual(self.answer.question, self.question)
        self.assertEqual(self.answer.text, 'text_answer')
        
        self.assertFalse(self.answer.audio_response)
        self.assertFalse(self.answer.is_correct)


        # 2 ответ
        self.assertEqual(self.answer_correct.question, self.question)
        self.assertEqual(self.answer_correct.text, 'text_answer_is_correct')
        self.assertEqual(self.answer_correct.is_correct, True)

        self.assertFalse(self.answer_correct.audio_response)


    def test_answer_max_lenght(self):
        with transaction.atomic():
            with self.assertRaises(DataError):
                name_answer = 'a' * 256

                Answer.objects.create(
                    question=self.question,
                    text=name_answer
                )

    def test_answer_str_method(self):
        self.assertEqual(self.answer.__str__(), 'text_answer')
        self.assertEqual(self.answer_correct.__str__(), 'text_answer_is_correct')

    def test_answer_delete_question_behavior(self):
        self.question.delete()
        with self.assertRaises(Answer.DoesNotExist):
            self.answer.refresh_from_db()
            self.answer_correct.refresh_from_db()
    
    def tearDown(self) -> None:
        self.user.delete()
        self.test.delete()
        if self.question.pk:
            self.question.delete()
        
        if self.answer.pk:
            self.answer.delete()
        
        if self.answer_correct.pk:
            self.answer_correct.delete()



class TestResultModelTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username='testuser')
        self.client.login(username='testuser')

        self.category = Categories.objects.create(name='testcategory', slug='test_category')

        self.test = Tests.objects.create(
            user=self.user,
            name='testname',
            category=self.category,
            description='test_description',
            check_type='auto',
            date_out=date(2021, 1, 4),
            duration=timedelta(seconds=55)
        )

        self.test_result_default = TestResult.objects.create(
            user=self.user,
            test=self.test,
            score = 0,
            date_taken=date(year=2024, month=10, day=26),
        )

        self.test_resut_set = TestResult.objects.create(
            user=self.user,
            test=self.test,
            score = 100,
            date_taken=date(year=2024, month=10, day=26),
            attempts=1,
            duration=timedelta(minutes=55,seconds=55),
            max_attempts=1,
            extra_attempts=0,
        )

    
    def test_testresult_create(self):
        # Проверяем тест со значениями по умолчанию
        self.assertEqual(self.test_result_default.user, self.user)
        self.assertEqual(self.test_result_default.test, self.test)
        self.assertEqual(self.test_result_default.score, 0)
        self.assertEqual(self.test_result_default.attempts, 1)
        self.assertEqual(self.test_result_default.max_attempts, 2)
        self.assertEqual(self.test_result_default.extra_attempts, 0)

        self.assertFalse(self.test_result_default.duration)

        # Проверяем тест с выставленными значениями
        self.assertEqual(self.test_resut_set.user, self.user)
        self.assertEqual(self.test_resut_set.test, self.test)
        self.assertEqual(self.test_resut_set.score, 100)
        self.assertEqual(self.test_resut_set.duration, timedelta(minutes=55, seconds=55))
        self.assertEqual(self.test_resut_set.attempts, 1)
        self.assertEqual(self.test_resut_set.max_attempts, 1)
        self.assertEqual(self.test_result_default.extra_attempts, 0)

    
    def test_str_and_remaining_attempts(self):
        self.assertEqual(self.test_resut_set.__str__(), f"{self.user.username} - {self.test.name} - {int(self.test_resut_set.score)}%")
        self.assertEqual(self.test_result_default.__str__(), f"{self.user.username} - {self.test.name} - {int(self.test_result_default.score)}%")

        self.assertEqual(int(self.test_resut_set.remaining_atemps), 0)
        self.assertEqual(int(self.test_result_default.remaining_atemps), 1)


    # def test_score_max_digits(self):
    #     with transaction.atomic():
    #         with self.assertRaises(DataError):
    #             TestResult.objects.create(
    #                 user=self.user,
    #                 test=self.test,
    #                 score=0.000000,
    #             )
    

    def test_testresult_delete_test_behavior(self):
        self.test.delete()
        with self.assertRaises(TestResult.DoesNotExist):
            self.test_resut_set.refresh_from_db()
            self.test_result_default.refresh_from_db()
        

    def tearDown(self) -> None:
        self.user.delete() 
        self.category.delete()

        if self.test.pk:
            self.test.delete()

    

class TestReviewsModelTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username='testuser')
        self.client.login(username='testuser')

        self.category = Categories.objects.create(name='testcategory', slug='test_category')

        self.test = Tests.objects.create(
            user=self.user,
            name='testname',
            category=self.category,
            description='test_description',
            check_type='auto',
            date_out=date(2021, 1, 4),
            duration=timedelta(seconds=55)
        )

        self.test_review_default = TestsReviews.objects.create(
            test=self.test,
            user=self.user,
            duration=timedelta(seconds=30),
            group='test_group',
            score=50,
            answers={'question_1':'1'}
        )


    def test_testreview_create(self):
        self.assertEqual(self.test_review_default.test, self.test)
        self.assertEqual(self.test_review_default.user, self.user)
        self.assertEqual(self.test_review_default.duration, timedelta(seconds=30))
        self.assertEqual(self.test_review_default.group, 'test_group')
        self.assertEqual(self.test_review_default.score, 50)
        self.assertEqual(self.test_review_default.answers, {'question_1': '1'})
        

        self.assertFalse(self.test_review_default.audio_answers)
        self.assertFalse(self.test_review_default.reviewed)

    def test_group_max_lenght(self):
        with transaction.atomic():
            with self.assertRaises(DataError):
                name_group = 'g' * 101

                TestsReviews.objects.create(
                    test=self.test,
                    user=self.user,
                    duration=timedelta(seconds=30),
                    group=name_group,
                    score=50,
                    answers={'question_1':'1'}
                )

    def test_testreview_delete_test_behavior(self):
        self.test.delete()
        with self.assertRaises(TestsReviews.DoesNotExist):
            self.test_review_default.refresh_from_db()

    
    def tearDown(self) -> None:
        self.user.delete()
        self.category.delete()
        
        if self.test.pk:
            self.test.delete()
        



class UserRatingViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        logged_in = self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(logged_in, "Login failed during setup for IndexViewTest")

        self.category  = Categories.objects.create(name='Cattest', slug='cattest')
        
        self.test_uncompleted = Tests.objects.create(
            user=self.user,
            name='Three Tets',
            description='Test description',
            category=self.category,  # Assuming you have categories, else leave as None
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            students={'students': [str(self.user.id)]}
        )

        self.test = Tests.objects.create(
            user=self.user,
            name='Sample Test',
            description='Test description',
            category=self.category,  # Assuming you have categories, else leave as None
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            students={'students': [str(self.user.id)]}
        )

        self.group = UsersGroup.objects.create(name='Test_group')
        self.group_membeship = UsersGroupMembership.objects.create(user=self.user,  group=self.group)

        self.completed_test = TestResult.objects.create(
            user=self.user,
            test=self.test,
            score = 0,
            date_taken=date(year=2024, month=10, day=26),
        )

    def test_user_rating(self):
        response = self.client.get(reverse('app:index'))
        self.assertEqual(response.status_code, 200)

    def test_user_rating_view_redirect_logout(self):
        self.client.logout()

        rating_url = reverse('tests:rating')
        response = self.client.get(rating_url)

        # Ожидаемый URL перенаправления
        expected_url = f"{reverse('users:login')}?next={rating_url}"

        self.assertRedirects(response, expected_url)

    def test_rating_view_template_name(self):
        response = self.client.get(reverse('tests:rating'))
        self.assertTemplateUsed(response, 'tests/rating.html')

    def test_rating_view_context_data(self):
        response = self.client.get(reverse('tests:rating'))
        
        self.assertIn('tests', response.context)
        self.assertIn('user', response.context)
        self.assertIn('active_tab', response.context)

        tests = response.context['tests']
        user = response.context['user']

        self.assertIn(self.test, tests)
        self.assertEqual(self.user, user)

    def tearDown(self) -> None:
        if self.test.pk:
            self.test.delete()
        self.category.delete()
        self.user.delete()


class RatingTestViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        logged_in = self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(logged_in, "Login failed during setup for IndexViewTest")

        self.category = Categories.objects.create(name='Cattest', slug='cattest')
        
        self.test_uncompleted = Tests.objects.create(
            user=self.user,
            name='Three Tets',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            students={'students': [str(self.user.id)]}
        )

        self.test = Tests.objects.create(
            user=self.user,
            name='Sample Test',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            students={'students': [str(self.user.id)]}
        )

        self.test_id = self.test.id

        self.group = UsersGroup.objects.create(name='Test_group')
        # Сохраняем членство в группе
        self.group_membership = UsersGroupMembership.objects.create(user=self.user, group=self.group)

        # Создаем результат теста
        self.completed_test = TestResult.objects.create(
            user=self.user,
            test=self.test,
            score=0,
            date_taken=date(year=2024, month=10, day=26),
            duration=timedelta(seconds=30)
        )
    
    def test_view_status_code(self):
        response = self.client.get(reverse('tests:rating_test', args=[self.test_id]))
        self.assertEqual(response.status_code, 200)

    def test_rating_test_redirect_loguot(self):
        self.client.logout()

        rating_url = reverse('tests:rating_test', args=[self.test_id])
        response = self.client.get(rating_url)

        # Ожидаемый URL перенаправления
        expected_url = f"{reverse('users:login')}?next={rating_url}"

        self.assertRedirects(response, expected_url)

    def test_rating_test_tesmplate_name(self):
        response = self.client.get(reverse('tests:rating_test', args=[self.test_id]))
        self.assertTemplateUsed(response, 'tests/rating_test.html')

    
    def test_rating_test_view_context(self):
        response = self.client.get(reverse('tests:rating_test', args=[self.test_id]))

        self.assertIn('test', response.context)
        self.assertIn('user', response.context)
        self.assertIn('results', response.context)
        self.assertIn('active_tab', response.context)

        test = response.context['test']
        user = response.context['user']
        results = response.context['results']

        self.assertEqual(self.test, test)
        self.assertEqual(self.user, user)

        self.assertIn(self.completed_test, results)

    def tearDown(self) -> None:
        self.completed_test.delete()
        self.test_uncompleted.delete()
        self.group_membership.delete()
        self.group.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()


class AllTestsViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        logged_in = self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(logged_in, "Login failed during setup for IndexViewTest")

        self.category = Categories.objects.create(name='Cattest', slug='cattest')
        
        self.test_uncompleted = Tests.objects.create(
            user=self.user,
            name='Three Tets',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            students={'students': [str(self.user.id)]}
        )

        self.test = Tests.objects.create(
            user=self.user,
            name='Sample Test',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            students={'students': [str(self.user.id)]}
        )


    def test_status_code_view(self):
        response = self.client.get(reverse('tests:all_tests'))
        self.assertEqual(response.status_code, 200)

    
    def test_all_tests_url(self):
        self.client.logout()

        all_test_url = reverse('tests:all_tests')
        response = self.client.get(all_test_url)

        # Ожидаемый URL перенаправления
        expected_url = f"{reverse('users:login')}?next={all_test_url}"

        self.assertRedirects(response, expected_url) 
    
    def test_all_test_tamplate_name(self):
        response = self.client.get(reverse('tests:all_tests'))
        self.assertTemplateUsed(response, 'tests/all_tests.html')

    
    def test_all_test_context(self):
        response = self.client.get(reverse('tests:all_tests'))

        self.assertIn('tests', response.context)
        self.assertIn('active_tab', response.context)

        tests = response.context['tests']

        self.assertIn(self.test_uncompleted, tests)
        self.assertIn(self.test, tests)

    
    def tearDown(self) -> None:
        self.test_uncompleted.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()


class CreateTestViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.group = UsersGroup.objects.create(name='Test_group')
        # Сохраняем членство в группе
        self.group_membership = UsersGroupMembership.objects.create(user=self.user, group=self.group)

    def test_view_access(self):
        response = self.client.get(reverse('tests:create_test'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tests/create_test.html')

    def test_form_submission_success(self):
        form_data = {
            'user': self.user.id,
            'name': "Test Name",
            'description': "Test Description",
            'category': self.category.id,
            'check_type': 'auto',
            'duration': "00:00:25",
            'raw_duration':'60хв',
            'date_out': date(year=2024, month=9, day=25),
        }

        response = self.client.post(reverse('tests:create_test'), data=form_data)

        # Проверка на ошибки формы
        if response.context and 'form' in response.context:
            form = response.context['form']
            if not form.is_valid():
                print("Ошибки формы:", form.errors)  # Вывод всех ошибок формы для диагностики

        # Проверка статуса и редиректа
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Tests.objects.filter(name='Test Name').exists())

        # Проверка данных теста
        created_test = Tests.objects.get(name="Test Name")
        self.assertEqual(created_test.user, self.user)

        self.assertEqual(created_test.duration, timedelta(hours=1))
        

        expected_url = reverse('tests:add_questions', kwargs={"test_id": created_test.id})
        self.assertRedirects(response, expected_url)

    
    def test_form_invalid_submission(self):
        # Данные формы
        form_data = {
            'user': self.user.id,
            'description': "Test Description",
            'students': [str(self.user.pk),],
            'category': self.category.id,
            'check_type': 'auto',
            'duration': "00:00:25",
            'date_out': date(year=2024, month=9, day=25),
        }

       # Проверяем валидацию формы напрямую
        form = TestForm(data=form_data)
        self.assertFalse(form.is_valid())  # Ожидаем, что форма не валидна
        self.assertIn('name', form.errors)  # Проверяем, что есть ошибка для 'name'

        # Теперь делаем запрос
        response = self.client.post(reverse('tests:create_test'), data=form_data)

        # Проверяем, что ответ корректный и шаблон соответствует ожидаемому
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tests/create_test.html')


class DeleteTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = Tests.objects.create(
            user=self.user,
            name='Sample Test',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            students={'students': [str(self.user.id)]},
            duration=timedelta(seconds=35)
        )

        self.test_id = self.test.pk

    
    def test_view_delete_test(self):
        response = self.client.get(reverse('tests:delete_test', args=[self.test_id]))
        self.assertFalse(Tests.objects.filter(name='Sample Test').exists())


        self.assertEqual(response.status_code, 302)
        
        expected_url = reverse('app:index')
        self.assertRedirects(response, expected_url)


class AddQuestionGroupViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = Tests.objects.create(
            user=self.user,
            name='Sample Test',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            students={'students': [str(self.user.id)]},
            duration=timedelta(seconds=35)
        )

        self.test_id = self.test.pk


    def test_add_question_group_view(self):
        response = self.client.get(reverse('tests:add_question_group', args=[self.test_id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tests/adq.html')

    def test_add_question_group_form_valid(self):

        form_data = {
            'name': "Sample test group",
            'test': self.test
        }

        response = self.client.post(reverse('tests:add_question_group', args=[self.test_id]), data=form_data)

        self.assertEqual(response.status_code, 302)

        self.assertTrue(QuestionGroup.objects.filter(name='Sample test group').exists())

        question_group = QuestionGroup.objects.filter(name='Sample test group').first()

        self.assertEqual(form_data['test'], question_group.test)

        expected_url = reverse('tests:add_questions', kwargs={"test_id": self.test_id})
        self.assertRedirects(response, expected_url)

    def test_form_ivalid(self):

        form_data = {
            'test': self.test,
        }

        # Проверяем валидацию формы напрямую
        form = QuestionGroupForm(data=form_data)
        self.assertFalse(form.is_valid())  # Ожидаем, что форма не валидна
        self.assertIn('name', form.errors)  # Проверяем, что есть ошибка для 'name'

        response = self.client.post(reverse('tests:add_question_group', args=[self.test_id]), data=form_data)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "tests/adq.html")


class AddQuestionViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = Tests.objects.create(
            user=self.user,
            name='Sample Test',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            duration=timedelta(seconds=35)
        )

        self.test_id = self.test.pk

        self.group = UsersGroup.objects.create(name='Test_group')
        # Сохраняем членство в группе
        self.group_membership = UsersGroupMembership.objects.create(user=self.user, group=self.group)

        self.question_group = QuestionGroup.objects.create(
            name='Test question group',
            test=self.test,
        )

    def test_template_name_and_status_code(self):
        response = self.client.get(reverse('tests:add_questions', args=[self.test_id]))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'tests/add_questions.html')

    
    def test_form_submission_valid(self):

        form_data_question_no_group = {
            'text': "question_text",
            'question_type': 'TXT',
            'form_type': 'form_question'
        }

        form_data_question_group = {
            'text': "question_text_group",
            'question_type': 'AUD',
            'form_type': 'form_question',
            'group': self.question_group.pk
        }

        form_data_students = {
            'students': [str(self.user.pk)],  # Обязательно как список, даже если один студент
            'form_type': 'form_student'
        }


        response_question_no_group = self.client.post(reverse('tests:add_questions', args=[self.test_id]), data=form_data_question_no_group)
        response_question_group = self.client.post(reverse('tests:add_questions', args=[self.test_id]), data=form_data_question_group)
        response_question_students = self.client.post(reverse('tests:add_questions', args=[self.test_id]), data=form_data_students)

        self.assertEqual(response_question_no_group.status_code, 302)
        self.assertEqual(response_question_group.status_code, 302)
        self.assertEqual(response_question_students.status_code, 302)

        self.assertTrue(Question.objects.filter(text='question_text').exists())
        self.assertTrue(Question.objects.filter(text='question_text_group').exists())

        self.test.refresh_from_db()

        self.assertIn(str(self.user.pk), self.test.students['students'])

        expected_url = reverse('tests:add_questions', args=[self.test_id])

        self.assertRedirects(response_question_no_group, expected_url)
        self.assertRedirects(response_question_group, expected_url)
        self.assertRedirects(response_question_students, expected_url)


    def test_add_question_context(self):
        # Создаем неупорядоченный вопрос и вопрос в группе для теста
        ungrouped_question = Question.objects.create(
            text="question_text",
            question_type="SC",
            test=self.test
        )

        group_question = Question.objects.create(
            text="question_text_group",
            question_type="MC",
            test=self.test,
            group=self.question_group
        )


        response = self.client.get(reverse('tests:add_questions', args=[self.test_id]))

        self.assertIn('test', response.context)
        self.assertIn('question_groups', response.context)
        self.assertIn('ungrouped_questions', response.context)
        self.assertIn('questions', response.context)
        self.assertIn('question_form', response.context)
        self.assertIn('form_student', response.context)

        ungrouped_question = Question.objects.filter(text="question_text").first()
        group_question = Question.objects.filter(text="question_text_group").first()

        test = response.context['test']
        question_groups = response.context['question_groups']
        ungrouped_questions = response.context['ungrouped_questions']
        questions = response.context['questions']

        self.assertEqual(self.test, test)

        self.assertIn(self.question_group, question_groups)
        self.assertIn(ungrouped_question, ungrouped_questions)

        self.assertIn(ungrouped_question, questions)
        self.assertIn(group_question, questions)

    def tearDown(self) -> None:
        self.question_group.delete()
        self.group_membership.delete()
        self.group.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()


class DeleteQuestionViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = Tests.objects.create(
            user=self.user,
            name='Sample Test',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            duration=timedelta(seconds=35)
        )

        self.test_id = self.test.pk

        self.question = Question.objects.create(
            test=self.test,
            text='Question text',
            question_type='MC',
        )

    def test_delete_question_view(self):
        response = self.client.get(reverse('tests:delete_question', args=[self.question.pk]))

        self.assertEqual(response.status_code, 302)

        self.assertFalse(Question.objects.filter(id=self.question.id))

        expected_url = reverse('tests:add_questions', args=[self.test_id])
        self.assertRedirects(response, expected_url)

    def tearDown(self) -> None:
        self.question.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()


class AddAnswerViewTest(TestCase):
    
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = Tests.objects.create(
            user=self.user,
            name='Sample Test',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            duration=timedelta(seconds=35)
        )

        self.test_id = self.test.pk

        self.question = Question.objects.create(
            test=self.test,
            text='Question text',
            question_type='MC',
        )
    

    def test_add_answer_to_question(self):
        form_data = {
            'text': '1 answer',
            'is_correct': False,
        }

        response = self.client.post(reverse('tests:add_answers', args=[self.question.pk]), data=form_data)

        self.assertEqual(response.status_code, 302)

        self.assertTrue(Answer.objects.filter(text='1 answer').first())

        answer = Answer.objects.filter(text='1 answer').first()

        self.assertEqual(self.question.id, answer.question.id)

        expected_url = reverse('tests:add_answers', args=[self.question.pk])
        self.assertRedirects(response, expected_url)


    def test_add_answer_context(self):
        response = self.client.get(reverse('tests:add_answers', args=[self.question.id]))

        self.assertEqual(response.status_code, 200)

        template_name = 'tests/add_answer.html'
        self.assertTemplateUsed(response, template_name)

        self.assertIn('test', response.context)
        self.assertIn('question', response.context)
        self.assertIn('questions',response.context)
        self.assertIn('form_type', response.context)
        self.assertIn('action_url', response.context)

        self.assertEqual(self.test, response.context['test'])
        self.assertEqual(self.question, response.context['question'])
        self.assertEqual('Ответ', response.context['form_type'])
        self.assertEqual('tests:add_answers', response.context['action_url'])

        self.assertIn(self.question, response.context['questions'])


    def test_add_answer_logout(self):
        self.client.logout()

        add_answer_url = reverse('tests:add_answers', args=[self.question.pk])
        response = self.client.get(add_answer_url)

        # Ожидаемый URL перенаправления
        expected_url = f"{reverse('users:login')}?next={add_answer_url}"

        self.assertRedirects(response, expected_url) 


    def test_add_answer_form_invalid(self):
        form_data = {
            'is_correct': True,
        }

        response = self.client.post(reverse('tests:add_answers', args=[self.question.pk]), data=form_data)

        self.assertEqual(response.status_code, 200)

         
        form = AnswerForm(data=form_data)
        self.assertFalse(form.is_valid())  # Ожидаем, что форма не валидна
        self.assertIn('text', form.errors)


    def tearDown(self) -> None:
        self.question.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()


class DeleteAnswerViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = Tests.objects.create(
            user=self.user,
            name='Sample Test',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            duration=timedelta(seconds=35)
        )

        self.test_id = self.test.pk

        self.question = Question.objects.create(
            test=self.test,
            text='Question text',
            question_type='MC',
        )

        self.answer = Answer.objects.create(
            question=self.question,
            text='Sample',
            is_correct=True,
        )

    def test_delete_anwer(self):
        response = self.client.get(reverse('tests:delete_answer', args=[self.answer.pk]))

        self.assertEqual(response.status_code, 302)

        self.assertFalse(Answer.objects.filter(text='Sample'))

        expected_url = reverse('tests:add_answers', args=[self.question.pk])
        self.assertRedirects(response, expected_url)

    def tearDown(self) -> None:
        self.answer.delete()
        self.question.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()


class MatchingPairViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = Tests.objects.create(
            user=self.user,
            name='Sample Test',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            duration=timedelta(seconds=35)
        )

        self.test_id = self.test.pk

        self.question = Question.objects.create(
            test=self.test,
            text='Question text',
            question_type='MC',
        )

    def test_matching_form_valid(self):
        form_data = {
            'left_item': 'left_test_item',
            'right_item': 'right_test_item',
        }

        response = self.client.post(reverse('tests:add_matching_pair', args=[self.question.pk]), data=form_data)

        self.assertEqual(response.status_code, 302)

        self.assertTrue(MatchingPair.objects.filter(left_item='left_test_item').exists())

        matching_pair = MatchingPair.objects.filter(left_item='left_test_item').first()
        self.assertEqual(self.question.pk, matching_pair.question.pk)

        expected_url = reverse('tests:add_matching_pair', args=[self.question.pk])
        self.assertRedirects(response, expected_url)

    def test_matching_pair_template(self):
        response = self.client.get(reverse('tests:add_matching_pair', args=[self.question.pk]))
        
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'tests/add_answer.html')

    def test_matching_form_invalid(self):
        form_data = {
            'right_item':'lob',
        }

        response = self.client.post(reverse('tests:add_matching_pair', args=[self.question.pk]), data=form_data)

        form = MatchingPairForm(data=form_data)
        self.assertFalse(form.is_valid())  # Ожидаем, что форма не валидна
        self.assertIn('left_item', form.errors)

    def test_matching_pair_context(self):
        response = self.client.get(reverse('tests:add_matching_pair', args=[self.question.pk]))

        self.assertIn('test', response.context)
        self.assertIn('question', response.context)
        self.assertIn('questions', response.context)
        self.assertIn('form_type', response.context)
        self.assertIn('action_url', response.context)

        self.assertEqual(self.test, response.context['test'])
        self.assertEqual(self.question, response.context['question'])
        self.assertEqual('Соотвецтвие', response.context['form_type'])
        self.assertEqual('tests:add_matching_pair', response.context['action_url'])

        self.assertIn(self.question, response.context['questions'])

    def tearDown(self) -> None:
        self.question.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()


class TestPreviewViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = Tests.objects.create(
            user=self.user,
            name='Sample Test',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            duration=timedelta(seconds=35)
        )

        self.test_id = self.test.pk

        self.test_review_default = TestsReviews.objects.create(
            test=self.test,
            user=self.user,
            duration=timedelta(seconds=30),
            group='test_group',
            score=50,
            answers={'question_1':'1'}
        )

        # Создаем результат теста
        self.completed_test = TestResult.objects.create(
            user=self.user,
            test=self.test,
            score=0,
            date_taken=date(year=2024, month=10, day=26),
            duration=timedelta(seconds=30)
        )

    
    def test_preview_context(self):
        response = self.client.get(reverse('tests:test_preview', args=[self.test_id]))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'tests/test_preview.html')

        self.assertIn('test', response.context)
        self.assertIn('test_results',  response.context)
        self.assertIn('required_attemps', response.context)
        self.assertIn('test_review', response.context)


        self.assertEqual(self.test, response.context['test'])
        self.assertEqual(True, response.context['required_attemps'])
        self.assertEqual(self.completed_test, response.context['test_results'])

        self.assertIn(self.test_review_default, response.context['test_review'])

    def tearDown(self) -> None:
        self.test_review_default.delete()
        self.completed_test.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()




class TakeTestViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = Tests.objects.create(
            user=self.user,
            name='Sample Test',
            description='Test description',
            category=self.category,
            check_type='auto',
            date_out=date(year=2024, month=10, day=25),
            duration=timedelta(seconds=35)
        )

        self.test_id = self.test.pk

        self.question_group = QuestionGroup.objects.create(name='Sample group', test=self.test)

        self.question = Question.objects.create(
            test=self.test,
            group=self.question_group,
            text='Question text',
            question_type='TXT',
            answer_type='SC'
        )

        self.question_2 = Question.objects.create(
            test=self.test,
            text='Question text two',
            question_type='TXT',
            answer_type='INP'

        )

        self.url = reverse('tests:take_test', kwargs={'test_id': self.test_id})

    def test_initialize_test_session(self):
        response = self.client.get(self.url)
        session = self.client.session
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('test_id', session)
        self.assertEqual(session['test_id'], self.test.id)
        self.assertIn('question_order', session)
        self.assertIn(self.question.id, session['question_order'])
        self.assertIn(self.question_2.id, session['question_order'])

    def test_display_question(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Question text')

    def test_submit_answer_and_move_to_next_question(self):
        self.choice_1 = Answer.objects.create(
            question=self.question,
            text='Choice 1',
            is_correct=True,
        )
        # Здесь предположим, что текущий вопрос — это Single Choice (SC)
        self.question.answer_type = 'SC'
        self.question.save()

        # Теперь тестируем отправку данных
        response = self.client.post(self.url, {
            'answer': self.choice_1.id,  # передаем правильный выбор в Single Choice
            'remaining_time': 1000,  # время
        })

        # Проверяем, что ответ на вопрос был сохранен
        session = self.client.session
        question_id_key = f'question_{self.question.id}'
        self.assertIn(question_id_key, session['test_responses'])

    def test_submit_multiple_choice_answer(self):
        self.choice_1 = Answer.objects.create(
            question=self.question,
            text='Choice 1',
            is_correct=True,
        )

        self.choice_2 = Answer.objects.create(
            question=self.question,
            text='Choice 2',
        )

        self.question.answer_type = 'MC'
        self.question.save()
        response = self.client.post(self.url, {
            'answer': [self.choice_1.id, self.choice_2.id],  # Несколько ответов для MC
            'remaining_time': 1000,
        })
        session = self.client.session
        question_id_key = f'question_{self.question.id}'
        self.assertIn(question_id_key, session['test_responses'])

    def test_submit_text_answer(self):
        self.question.answer_type = 'INP'
        self.question.save()
        response = self.client.post(self.url, {
            'answer': 'Sample text answer',
            'remaining_time': 1000,
        })
        session = self.client.session
        question_id_key = f'question_{self.question.id}'
        self.assertIn(question_id_key, session['test_responses'])

    def test_submit_matching_answer(self):
        self.question.question_type = 'MTCH'
        self.question.save()
        response = self.client.post(self.url, {
            'answer': {
                'matching_left_1': 'matching_right_1', 
                'matching_left_2': 'matching_right_2'
            },
            'remaining_time': 1000,
        })
        session = self.client.session
        question_id_key = f'question_{self.question.id}_type_matching'
        self.assertIn(question_id_key, session['test_responses'])

    def test_complete_test(self):
        self.choice_1 = Answer.objects.create(
            question=self.question,
            text='Choice 1',
            is_correct=True,
        )
        
        # Проверяем по конфигу тестов, то есть 1-й TXT|SC 2-й TXT|INP
        self.client.get(self.url)

         # Отвечаем на первый вопрос
        self.client.post(self.url, {
            'answer': self.choice_1.id,
            'remaining_time': 1800,
        })
        
        # Отвечаем на второй вопрос (последний)
        response = self.client.post(self.url, {
            'answer': 'Answer for question 2',
            'remaining_time': 1700,
        })

        self.assertRedirects(response, reverse('tests:test_results', kwargs={'test_id': self.test.id}))