from django.contrib.auth import get_user_model
from django.db import DataError, IntegrityError, transaction
from django.test import TestCase
from datetime import date, timedelta

from django.urls import reverse


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
        question_type = [Question.SINGLE_CHOICE, Question.MULTIPLE_CHOICE, Question.INPUT, Question.MATCHING, Question.AUDIO]
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
        self.group_membeship = UsersGroupMembership(user=self.user,  group=self.group)

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