from django.contrib.auth import get_user_model
from django.db import DataError, IntegrityError, transaction
from django.test import TestCase
from datetime import date, timedelta

from tests.models import (Answer,
                        Categories, 
                        MatchingPair, 
                        Question, 
                        QuestionGroup, 
                        TestResult, 
                        Tests, 
                        TestsReviews)

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
        self.assertEqual(str(self.question), f"Дата та назва тесту: {self.question.test.date_taken.date()} - {self.question.test.name}|  Питання: {self.question.text}" or f"Дата та назва тесту: {self.question.test.date_taken.date()} - {self.question.test.name}| Питання: {self.question.question_type} - {self.question.id}")
        self.assertEqual(str(self.question_in_group), f"Дата та назва тесту: {self.question_in_group.test.date_taken.date()} - {self.question_in_group.test.name}|  Питання: {self.question_in_group.text}" or f"Дата та назва тесту: {self.question_in_group.test.date_taken.date()} - {self.question_in_group.test.name}| Питання: {self.question_in_group.question_type} - {self.question_in_group.id}")

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
        self.assertEqual(self.matching.__str__(), f'Питання: {self.question.question_info}| Відповідність: {self.matching.left_item} - {self.matching.right_item}')

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
        self.assertEqual(self.answer.__str__(), f'Питання: {self.question.question_info}| Відповідь: {self.answer.text}')
        self.assertEqual(self.answer_correct.__str__(), f'Питання: {self.question.question_info}| Відповідь: {self.answer_correct.text}')

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