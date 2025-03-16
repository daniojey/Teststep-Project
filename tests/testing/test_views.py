from decimal import Decimal
from tokenize import group
from django.shortcuts import redirect
from django.utils.timezone import localtime, now
from tkinter.messagebox import QUESTION
from django.contrib.auth import get_user_model, login
from django.template.defaultfilters import first
from django.test import TestCase
from datetime import date, timedelta, timezone

from django.urls import reverse
from django.utils import duration
from django.utils.timezone import localtime
from httpx import delete
from tests.factories import AudioFactory, ImageFactory, TestFactory
from tests.forms import AnswerForm, MatchingPairForm, QuestionForm, QuestionGroupForm, TestForm


from tests.models import Answer, Categories, MatchingPair, Question, QuestionGroup, TestResult, Tests, TestsReviews
from users.models import UsersGroup, UsersGroupMembership

# Create your tests here.

User = get_user_model()

class HomePageViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        logged_in = self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(logged_in, "Login failed during setup for HomePageViewTest")

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
        self.group_membeship = UsersGroupMembership.objects.create(user=self.user,  group=self.group, owner=True)

        self.completed_test = TestResult.objects.create(
            user=self.user,
            test=self.test,
            score = 0,
            date_taken=date(year=2024, month=10, day=26),
            duration=timedelta(hours=2),
        )

    def test_user_rating(self):
        """Проверяем что пользователь может зайти на страничку рейтинга"""
        response = self.client.get(reverse('tests:rating'))
        self.assertEqual(response.status_code, 200)

    

    def test_user_rating_view_redirect_logout(self):
        """Проверяем происходит ли редирект на страницу 
        логина при попытке перехода на ссылку странички рейтинга"""
        self.client.logout()

        rating_url = reverse('tests:rating')
        response = self.client.get(rating_url)

        self.assertEqual(response.status_code, 302)

        # Ожидаемый URL перенаправления
        expected_url = f"{reverse('users:login')}?next={rating_url}"

        self.assertRedirects(response, expected_url)

    def test_rating_view_template_name(self):
        """Проверяем используемый шаблон"""
        response = self.client.get(reverse('tests:rating'))
        self.assertTemplateUsed(response, 'tests/rating.html')

    def test_rating_view_context_data(self):
        """Проверяем наличие контекстных переменных и данных в нём"""
        response = self.client.get(reverse('tests:rating'))
        
        self.assertIn('user', response.context)

        self.assertIn('tests', response.context)
        self.assertIn('active_tab', response.context)

        tests = response.context['tests']
        user = response.context['user']
        active_tab = response.context['active_tab']

        self.assertIn(self.test, tests)
        self.assertIn(self.test_uncompleted, tests)
        self.assertEqual(self.user, user)
        self.assertEqual('rating', active_tab)

    def tearDown(self):
        if self.test.pk:
            self.test.delete()
        
        self.test_uncompleted.delete()
        self.completed_test.delete()
        self.category.delete()
        self.group_membeship.delete()
        self.group.delete()
        self.user.delete()


class RatingTestViewTest(TestCase): 

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        logged_in = self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(logged_in, "Login failed during setup for RatingTestViewTest")

        self.category = Categories.objects.create(name='Cattest', slug='cattest')       

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

        self.completed_test = TestResult.objects.create(
            user=self.user,
            test=self.test,
            score = 0,
            date_taken=date(year=2024, month=10, day=26),
            duration=timedelta(hours=2),
        )

    def test_view_status_code(self):
        """Проверяем Что переход залогиненого пользователя возвращает код 200(Успех)"""
        response = self.client.get(reverse('tests:rating_test', args=[self.test_id]))
        self.assertEqual(response.status_code, 200)

    def test_rating_test_redirect_loguot(self):
        """Проверяем что при вылогине и попытке перехода снова на страницу рейтинга по тесту 
        пользователь будет перенаправлен на страницу логина"""
        self.client.logout()

        rating_url = reverse('tests:rating_test', args=[self.test_id])
        response = self.client.get(rating_url)

        self.assertEqual(response.status_code, 302)

        # Ожидаемый URL перенаправления
        expected_url = f"{reverse('users:login')}?next={rating_url}"

        self.assertRedirects(response, expected_url)

    def test_rating_test_tesmplate_name(self):
        """ Проверяем что используется правильный шаблон"""
        response = self.client.get(reverse('tests:rating_test', args=[self.test_id]))
        self.assertTemplateUsed(response, 'tests/rating_test.html')

    
    def test_rating_test_view_context(self):
        """"""
        response = self.client.get(reverse('tests:rating_test', args=[self.test_id]))

        self.assertIn('test', response.context)
        self.assertIn('user', response.context)
        self.assertIn('results', response.context)
        self.assertIn('active_tab', response.context)

        test = response.context['test']
        user = response.context['user']
        results = response.context['results']
        active_tab = response.context['active_tab']

        self.assertEqual(self.test, test)
        self.assertEqual(self.user, user)
        self.assertEqual('rating', active_tab)

        self.assertIn(self.completed_test, results)

    def tearDown(self) -> None:
        self.completed_test.delete()
        self.group_membership.delete()
        self.group.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()


class AllTestsViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        logged_in = self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(logged_in, "Login failed during setup for AllTestsViewTest")

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
        """Проверяем Что переход залогиненого пользователя возвращает код 200(Успех)"""
        response = self.client.get(reverse('tests:all_tests'))
        self.assertEqual(response.status_code, 200)

    
    def test_all_tests_logout_user_test(self):
        """Проверяем что при вылогине и попытке перехода снова на страницу рейтинга по тесту 
        пользователь будет перенаправлен на страницу логина"""
        self.client.logout()

        all_test_url = reverse('tests:all_tests')
        response = self.client.get(all_test_url)

        # Ожидаемый URL перенаправления
        expected_url = f"{reverse('users:login')}?next={all_test_url}"

        self.assertRedirects(response, expected_url) 

    
    def test_all_test_tamplate_name(self):
        """Проверяем использование правильного шаблона"""
        response = self.client.get(reverse('tests:all_tests'))
        self.assertTemplateUsed(response, 'tests/all_tests.html')

    
    def test_all_test_context(self):
        """Проверяем наличие контекста и данные которые должны оказатся в контексте"""
        response = self.client.get(reverse('tests:all_tests'))

        self.assertIn('tests', response.context)
        self.assertIn('active_tab', response.context)

        tests = response.context['tests']
        active_tab = response.context['active_tab']

        self.assertIn(self.test_uncompleted, tests)
        self.assertIn(self.test, tests)
        self.assertEqual('my_tests', active_tab)

    
    def tearDown(self) -> None:
        self.test_uncompleted.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()


class CreateTestViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        loged_in = self.client.login(username='testuser', password='testpass')
        self.assertTrue(loged_in, "Login failed during setup for CreateTestViewTest")

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.group = UsersGroup.objects.create(name='Test_group')
        # Сохраняем членство в группе
        self.group_membership = UsersGroupMembership.objects.create(user=self.user, group=self.group)

    def test_view_status_code(self):
        """Проверяем статус код при попытке зайти на страницу"""
        response = self.client.get(reverse('tests:create_test'))
        self.assertEqual(response.status_code, 200)

    def test_view_user_template(self):
        """Проверяем используется ли правильный шаблон"""
        response = self.client.get(reverse('tests:create_test'))
        self.assertTemplateUsed(response, 'tests/create_test.html')

    def test_form_submission_success(self):
        """Проверяем что тест создаётся верно"""
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
        self.assertEqual(created_test.description, "Test Description")
        self.assertEqual(created_test.category, self.category)
        self.assertEqual(created_test.check_type, Tests.AUTO_CHECK)
        self.assertEqual(created_test.duration.total_seconds(), 3600)
        self.assertEqual(localtime(created_test.date_out).date(), date(year=2024, month=9, day=25))

        self.assertEqual(created_test.duration, timedelta(hours=1))

        expected_url = reverse('tests:add_questions', kwargs={"test_id": created_test.id})
        self.assertRedirects(response, expected_url)

    
    def test_form_invalid_submission(self):
        # Данные формы
        form_data = {
            'user': self.user.id,
            'description': "Test Description",
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

    def tearDown(self):
        self.group_membership.delete()
        self.group.delete()
        self.category.delete()
        if self.user:
            self.user.delete()

# TODO Продолжить переделку
class DeleteTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        logid_in = self.client.login(username='testuser', password='testpass')
        self.assertTrue(logid_in, "Login failed during setup for DeleteTest")

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

    
    def test_view_delete_test(self):
        response = self.client.get(reverse('tests:delete_test', args=[self.test_id]))
        self.assertFalse(Tests.objects.filter(name='Sample Test').exists())

        self.assertEqual(response.status_code, 302)
        
        expected_url = reverse('app:index')
        self.assertRedirects(response, expected_url)

    def tearDown(self):
        self.test.delete()
        self.category.delete()
        if self.user:
            self.user.delete()


class AddQuestionGroupViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        login_in = self.client.login(username='testuser', password='testpass')
        self.assertTrue(login_in ,"Login failed during setup for AddQuestionGroupViewTest")

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
        self.assertEqual(form_data['name'], question_group.name)

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
    
    def tearDown(self):
        self.test.delete()
        self.category.delete()
        if self.user:
            self.user.delete()


class AddQuestionViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        login_in = self.client.login(username='testuser', password='testpass')
        self.assertTrue(login_in, "Login failed during setup for AddQuestionViewTest")

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
        # TODO после того как будет реализовано ограничение переделать эту часть тестов
        # TODO Сделать проверку в модели чтобы при AUD типе вопроса добавление аудио было обязательным

        form_data_question_no_group = {
            'text': "question_text", # Является необязательным параметром
            'question_type': 'TXT',
            'form_type': 'form_question',
            'answer_type': "SC", # На данный момент не обязательное поле
        }

        form_data_question_group = {
            'text': "question_text_group", # Является необязательным параметром
            'question_type': 'AUD',
            'form_type': 'form_question',
            'group': self.question_group.pk,
            'answer_type': "MC", # На данный момент не обязательное поле
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
        self.assertEqual(response_question_students.status_code, 200) # Переадресации происходить не должно

        self.assertTrue(Question.objects.filter(text='question_text').exists())
        self.assertTrue(Question.objects.filter(text='question_text_group').exists())

        question_no_group = Question.objects.filter(text='question_text').first()
        question_add_group = Question.objects.filter(text='question_text_group').first()

        # Проверяем question_no_group
        self.assertEqual(question_no_group.test, self.test)
        self.assertEqual(question_no_group.text, form_data_question_no_group['text'])
        self.assertEqual(question_no_group.question_type, Question.TEXT)
        self.assertEqual(question_no_group.answer_type, Question.SINGLE_CHOICE)
        
        self.assertFalse(question_no_group.group)
        self.assertFalse(question_no_group.image)
        self.assertFalse(question_no_group.audio)

        # Проверяем question_add_group
        self.assertEqual(question_add_group.test, self.test)
        self.assertEqual(question_add_group.text, form_data_question_group['text'])
        self.assertEqual(question_add_group.question_type, Question.AUDIO)
        self.assertEqual(question_add_group.answer_type, Question.MULTIPLE_CHOICE)
        self.assertEqual(question_add_group.group, self.question_group)

        self.assertFalse(question_add_group.image)
        self.assertFalse(question_add_group.audio)

        # Проверяем наличие добавление студентов после отправки формы
        self.test.refresh_from_db()

        self.assertIn(str(self.user.pk), self.test.students['students'])

        expected_url = reverse('tests:add_questions', args=[self.test_id])

        self.assertRedirects(response_question_no_group, expected_url)
        self.assertRedirects(response_question_group, expected_url)
        

    def test_add_question_context(self):
        # Создаем неупорядоченный вопрос и вопрос в группе для теста
        image = ImageFactory.create_image('def.jpeg')
        image.name = "def.jpeg"  # Принудительно указываем имя
        # TODO разобратся почему при сохнарении image появляется приставка _<suffix>

        ungrouped_question = Question.objects.create(
            text="question_text",
            question_type="TXT",
            answer_type="SC",
            test=self.test
        )

        group_question = Question.objects.create(
            text="question_text_group",
            question_type="IMG",
            answer_type="MC",
            test=self.test,
            group=self.question_group,
            image=image #Создаём изображение в 3мб
        )

        audio_question = Question.objects.create(
            text="question_audio",
            question_type="TXT",
            answer_type="AUD",
            test=self.test,
            audio=AudioFactory.create_audio(filename="aud.mp3")
        )

        response = self.client.get(reverse('tests:add_questions', args=[self.test_id]))
        self.assertIn('test', response.context)
        self.assertIn('question_groups', response.context)
        self.assertIn('ungrouped_questions', response.context)
        self.assertIn('question_form', response.context)
        self.assertIn('form_student', response.context)

        ungrouped_question = Question.objects.filter(text="question_text").first()
        group_question = Question.objects.filter(text="question_text_group").first()
        aud_question = Question.objects.filter(text="question_audio").first()

        # Проверяем ungrouped_question
        self.assertEqual(ungrouped_question.text, 'question_text')
        self.assertEqual(ungrouped_question.question_type, Question.TEXT)
        self.assertEqual(ungrouped_question.answer_type, Question.SINGLE_CHOICE)
        self.assertEqual(ungrouped_question.test, self.test)
        self.assertFalse(ungrouped_question.image)
        self.assertFalse(ungrouped_question.audio)
        self.assertFalse(ungrouped_question.group)

        # Проверяем group_question
        self.assertEqual(group_question.text, 'question_text_group')
        self.assertEqual(group_question.question_type, Question.IMAGE)
        self.assertEqual(group_question.answer_type, Question.MULTIPLE_CHOICE)
        self.assertEqual(group_question.test, self.test)
        self.assertEqual(group_question.group, self.question_group)

        self.assertTrue(group_question.image)
        image_name = group_question.image.name.split('/')[-1].split('_')[0].split('.')[0]
        self.assertEqual(image_name, 'def')

        self.assertFalse(group_question.audio)

        # Проверяем aud_question
        self.assertEqual(aud_question.text, 'question_audio')
        self.assertEqual(aud_question.question_type, Question.TEXT)
        self.assertEqual(aud_question.answer_type, Question.ANSWER_AUDIO)
        self.assertEqual(aud_question.test, self.test)

        self.assertTrue(aud_question.audio)
        aud_name = aud_question.audio.name.split('/')[-1].split('_')[0].split('.')[0]
        self.assertEqual(aud_name, 'aud')

        self.assertFalse(aud_question.image)
        self.assertFalse(aud_question.group)


        test = response.context['test']
        question_groups = response.context['question_groups']
        ungrouped_questions = response.context['ungrouped_questions']

        self.assertEqual(self.test, test)

        self.assertIn(self.question_group, question_groups)
        self.assertIn(ungrouped_question, ungrouped_questions)
        self.assertIn(self.question_group, question_groups)
    
    def test_add_question_form_invalid(self):
        form_data = {
            'text': "question_text", # Является необязательным параметром
            'form_type': 'form_question',
            'answer_type': "SC", # На данный момент не обязательное поле
        }

        form = QuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("question_type", form.errors)

        response = self.client.post(reverse('tests:add_questions', args=[self.test_id]), data=form_data)

        self.assertEqual(response.status_code, 200)

    def test_add_question_logout(self):
        self.client.logout()
        add_question_url = reverse('tests:add_questions', args=[self.test_id])
        response = self.client.get(add_question_url)

        self.assertEqual(response.status_code, 302)

        expected_url= f"{reverse('users:login')}?next={add_question_url}"
        
        self.assertRedirects(response, expected_url)


    def tearDown(self) -> None:
        self.question_group.delete()
        self.group_membership.delete()
        self.group.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()

# Next change tests
class DeleteQuestionViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        login_in = self.client.login(username='testuser', password='testpass')
        self.assertTrue(login_in, "Login failed during setup for DeleteQuestionViewTest")

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = TestFactory(
            user=self.user, 
            category=self.category,
            name='Sample Test',
            description='Test description',
            date_out=date(year=2024, month=10, day=25),
            duration=timedelta(seconds=35)
        )

        # self.test = Tests.objects.create(
        #     user=self.user,
        #     name='Sample Test',
        #     description='Test description',
        #     category=self.category,
        #     check_type='auto',
        #     date_out=date(year=2024, month=10, day=25),
        #     duration=timedelta(seconds=35)
        # )

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
        login_in = self.client.login(username='testuser', password='testpass')
        self.assertTrue(login_in, "Login failed during setup for AddAnswerViewTest")

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

        self.assertIn('question', response.context)
        self.assertIn('form_type', response.context)
        self.assertIn('action_url', response.context)

        self.assertEqual(self.question, response.context['question'])
        self.assertEqual('Ответ', response.context['form_type'])
        self.assertEqual('tests:add_answers', response.context['action_url'])



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
        login_in = self.client.login(username='testuser', password='testpass')
        self.assertTrue(login_in, "Login failed during setup for DeleteAnswerViewTest")

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
        login_in = self.client.login(username='testuser', password='testpass')
        self.assertTrue(login_in, "Login failed during setup for MatchingPairViewTest")

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
            question_type='MTCH',
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
        self.assertEqual(matching_pair.left_item, "left_test_item")
        self.assertEqual(matching_pair.right_item, "right_test_item")

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
        self.assertIn('form_type', response.context)
        self.assertIn('action_url', response.context)

        self.assertEqual(self.test, response.context['test'])
        self.assertEqual(self.question, response.context['question'])
        self.assertEqual('Соотвецтвие', response.context['form_type'])
        self.assertEqual('tests:add_matching_pair', response.context['action_url'])

    def test_matching_pair_logout(self):
        self.client.logout()
        matching_pair_url = reverse('tests:add_matching_pair', args=[self.question.pk])
        response = self.client.get(matching_pair_url)

        self.assertEqual(response.status_code, 302)

        expected_url = f"{reverse('users:login')}?next={matching_pair_url}"
        self.assertRedirects(response, expected_url)

    def tearDown(self) -> None:
        self.question.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()


class TestPreviewViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        login_in =  self.client.login(username='testuser', password='testpass')
        self.assertTrue(login_in, "Login failed during setup for TestPreviewViewTest")

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

        self.url = reverse('tests:test_preview', args=[self.test_id])
    def test_preview_context(self):
        response = self.client.get(reverse('tests:test_preview', args=[self.test_id]))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'tests/test_preview.html')

        self.assertIn('test', response.context)
        self.assertIn('test_results',  response.context)
        self.assertIn('test_review', response.context)


        self.assertEqual(self.test, response.context['test'])
        self.assertEqual(self.completed_test, response.context['test_results'])

        self.assertIn(self.test_review_default, response.context['test_review'])
    
    def test_test_preview_logout(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

        expected_url =  f"{reverse('users:login')}?next={self.url}"
        self.assertRedirects(response, expected_url)

    def tearDown(self):
        self.test_review_default.delete()
        self.completed_test.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()


class TakeTestViewTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='testpass')
        login_in = self.client.login(username='testuser', password='testpass')
        self.assertTrue(login_in, "Login failed during setup for TakeTestViewTest")

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
        self.assertTemplateUsed("tests/question.html")
        self.assertIn('test_id', session)
        self.assertEqual(session['test_id'], self.test.id)
        self.assertIn('question_order', session)
        self.assertIn(self.question.id, session['question_order'])
        self.assertIn(self.question_2.id, session['question_order'])

    def test_display_question_and_context(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context['test'], self.test)
        self.assertEqual(response.context['question'], self.question)
        self.assertEqual(response.context['all_questions']['current'], 1)
        self.assertEqual(response.context['all_questions']['all'], 2)
        self.assertEqual(response.context['test_btn']['text_btn'], 'Далі')
        self.assertEqual(response.context['current_question_group'], self.question_group)
        self.assertTrue(response.context['remaining_time'])
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
        response_two = self.client.get(self.url)
        self.assertEqual(response_two.context['test'], self.test)
        self.assertEqual(response_two.context['question'], self.question_2)
        self.assertEqual(response_two.context['all_questions']['current'], 2)
        self.assertEqual(response_two.context['all_questions']['all'], 2)
        self.assertEqual(response_two.context['test_btn']['text_btn'], 'Завершити')
        self.assertFalse(response_two.context['current_question_group'])
        self.assertTrue(response_two.context['remaining_time'])

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

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tests:test_results', kwargs={'test_id': self.test.id}))

    def test_take_test_logout(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

        expected_url =  f"{reverse('users:login')}?next={self.url}"
        self.assertRedirects(response, expected_url)

    def tearDown(self):
        self.question_2.delete()
        self.question.delete()
        self.question_group.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()

        if self.client.session:
            self.client.session.clear()


class TestResultsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        login_in = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_in, "Login failed during setup for TestResultsViewTest")


        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = TestFactory(
            user=self.user,
            category=self.category,
            date_out=date(year=2024, month=10, day=25),
            duration=timedelta(minutes=30)
            # click TestFactory and press F12 addition info 
        )

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
            answer_type='MC'
        )

        self.question_3 = Question.objects.create(
            test=self.test,
            text='Question text three',
            question_type='TXT',
            answer_type='INP'

        )

        # question
        self.answer_1_1 = Answer.objects.create(
            question=self.question,
            text="question answer 1",
            is_correct=True,
        )

        self.answer_1_2 = Answer.objects.create(
            question=self.question,
            text="question answer 2",
            # is_correct default False
        )

        # question_2
        self.answer_2_1 = Answer.objects.create(
            question=self.question_2,
            text="question_2 answer 1",
            is_correct=True,
        )

        self.answer_2_2 = Answer.objects.create(
            question=self.question_2,
            text="question_2 answer 2",
            is_correct=True,
        )

        self.answer_2_3 = Answer.objects.create(
            question=self.question_2,
            text="question_2 answer 3",
            # is_correct default False
        )

        # question_3
        self.answer_3_1 = Answer.objects.create(
            question=self.question_3,
            text="Success",
            is_correct=True,
        )

        self.test_manual = TestFactory(
            name="Manual test",
            user=self.user,
            category=self.category,
            date_out=date(year=2024, month=10, day=25),
            duration=timedelta(minutes=40),
            check_type=Tests.MANUAL_CHECK,
            # click TestFactory and press F12 addition info 
        )

        self.question_manual = Question.objects.create(
            test=self.test_manual,
            text='Question text',
            question_type='TXT',
            answer_type='SC'
        )

        self.asnwer_manual_1 = Answer.objects.create(
            question=self.question_manual,
            text="answer_manual 1",
            is_correct=True,
        )

        self.asnwer_manual_2 = Answer.objects.create(
            question=self.question_manual,
            text="answer_manual 2",
        )


        self.url = reverse("tests:test_results", kwargs={'test_id': self.test.id})

        self.url_manual = reverse("tests:test_results", kwargs={'test_id': self.test_manual.id})

    def test_create_results_in_test(self):
        # Явное сохранение сессии
        session = self.client.session
        session['test_responses'] = {
            f"question_{self.question.id}": str(self.answer_1_1.id),
            f"question_{self.question_2.id}": [str(self.answer_2_1.id), str(self.answer_2_2.id)],
            f"question_{self.question_3.id}": "Success",
        }
        session['remaining_time'] = 900
        session.save()  # Сохраняем сессию

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tests/test_results.html")

        result = TestResult.objects.get(user=self.user, test=self.test)

        self.assertEqual(result.user, self.user)
        self.assertEqual(result.test, self.test)
        self.assertEqual(result.score, Decimal(100.00))
        self.assertEqual(localtime(result.date_taken).date(), now().date())
        self.assertEqual(result.duration, timedelta(minutes=15))
        self.assertEqual(result.attempts, 1)
        self.assertEqual(result.max_attempts, 2)
        self.assertEqual(result.extra_attempts, 0)

        try_response = self.client.get(self.url)
        self.assertEqual(try_response.status_code, 302)
        self.assertRedirects(try_response, reverse('app:index'))


    def test_null_data_results(self):
        session = self.client.session
        session['test_responses'] = {
        }
        session['remaining_time'] = 900
        
        session.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        obj = TestResult.objects.get(user=self.user, test=self.test)

        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.test, self.test)
        self.assertEqual(obj.score, Decimal(0))
        self.assertEqual(obj.duration, timedelta(minutes=15))

        try_response = self.client.get(self.url)
        self.assertEqual(try_response.status_code, 302)
        self.assertRedirects(try_response, reverse('app:index'))

    def test_null_remaining_time_results(self):
        session = self.client.session
        session['test_responses'] = {
        }
        session['remaining_time'] = False
        
        session.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("app:index"))

    def test_create_test_reviews(self):
        # Явное сохранение сессии
        session = self.client.session
        session['test_responses'] = {
            f"question_{self.question_manual.id}": str(self.asnwer_manual_2.id) 
        }
        session['remaining_time'] = 900
        session.save()  # Сохраняем сессию

        response = self.client.get(self.url_manual)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tests/success_page_manual_test.html')

        obj = TestsReviews.objects.get(test=self.test_manual, user=self.user)

        self.assertEqual(obj.test, self.test_manual)
        self.assertEqual(obj.user, self.user)
        self.assertEqual(obj.duration, timedelta(minutes=25))
        self.assertEqual(obj.answers, {f"question_{self.question_manual.id}": str(self.asnwer_manual_2.id)})
        self.assertFalse(obj.audio_answers)

        try_response = self.client.get(self.url_manual)
        self.assertEqual(try_response.status_code, 302)
        self.assertRedirects(try_response, reverse("app:index"))

    def test_null_data_reviews(self):
        """Так как нам нужно не допускать пустое поле answers в экземплярах TestReviews
        мы при отсуцтвии либо времени либо ответов перенаправляем пользователя на начальную страницу"""
        session = self.client.session
        session['test_responses'] = {
             
        }
        session['remaining_time'] = 900
        session.save()  # Сохраняем сессию

        response = self.client.get(self.url_manual)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("app:index"))
    
    def tearDown(self):
        self.asnwer_manual_1.delete()
        self.asnwer_manual_2.delete()
        self.question_manual.delete()
        self.test_manual.delete()
        self.answer_3_1.delete()
        self.answer_2_3.delete()
        self.answer_2_2.delete()
        self.answer_2_1.delete()
        self.answer_1_2.delete()
        self.answer_1_1.delete()
        self.question_3.delete()
        self.question_2.delete()
        self.question.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()


class TestsForReviewVIewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username="testuser", password="testpass123")
        login_in = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_in, "Login failed during setup for TestResultsViewTest")

        self.user_test_1 = User.objects.create_user(username="testuser1", password="testpass123")
        self.user_test_2 = User.objects.create_user(username="testuser2", password="testpass123")

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = TestFactory(
            user=self.user,
            category=self.category,
            date_out=date(year=2024, month=10, day=25),
            duration=timedelta(minutes=30),
            check_type=Tests.MANUAL_CHECK,
            # click TestFactory and press F12 addition info 
        )

        self.group = UsersGroup.objects.create(name='Test_group')
        # Сохраняем членство в группе
        self.group_membership = UsersGroupMembership.objects.create(user=self.user, group=self.group)
        UsersGroupMembership.objects.create(user=self.user_test_1, group=self.group)
        UsersGroupMembership.objects.create(user=self.user_test_2, group=self.group)

        self.user_no_group = User.objects.create_superuser(username="testuser3", password="testpass123")

        self.user_no_valid = User.objects.create_user(username="testuser4", password="testpass123")

        self.url = reverse("tests:tests_for_review")
    def test_view_status_code(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tests/test_for_reviews.html")

        # self.assertRedirects(response, reverse("app:index"))

    def test_view_context_response(self):
        response = self.client.get(self.url)

        self.assertIn("test_result", response.context)
        self.assertIn("active_tab", response.context)

        test_result = response.context['test_result']
        active_tab = response.context['active_tab']

        self.assertIn(self.test, test_result)
        self.assertEqual('my_tests', active_tab)

    def test_user_no_group(self):
        self.client.logout()

        self.client.login(username="testuser3", password="testpass123")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_user_no_valid(self):
        self.client.logout()

        self.client.login(username='testuser4', password='testpass123')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("app:index"))

    def tearDown(self):
        self.user_no_valid.delete()
        self.user_no_group.delete()
        self.group_membership.delete()
        self.group.delete()
        self.test.delete()
        self.category.delete()
        self.user.delete()

class TestGroupReviewsViewTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        login_in = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_in, "Login failed during setup for TestResultsViewTest")

        self.test_user = User.objects.create(username="testuser1", password='testpass123')

        self.category = Categories.objects.create(name='Test_Cat', slug='test_cat')

        self.test = TestFactory(
            user=self.user,
            category=self.category,
            date_out=date(year=2024, month=10, day=25),
            duration=timedelta(minutes=30)
            # click TestFactory and press F12 addition info 
        )

        self.question = Question.objects.create(
            test=self.test,
            text='Question text',
            question_type='TXT',
            answer_type='SC'
        )

        self.answer = Answer.objects.create(
            question=self.question,
            text="Answer 1",
            is_correct=True,
        )

        self.group =  UsersGroup.objects.create(
            name="Test group"
        )

        self.group_membership = UsersGroupMembership.objects.create(
            user=self.user,
            group=self.group,
            owner=True,
        )

        UsersGroupMembership.objects.create(
            user=self.test_user,
            group=self.group,
            owner=True,
        )

        self.test_review = TestsReviews.objects.create(
            test=self.test,
            user=self.user,
            duration=timedelta(minutes=10),
            answers={f"question_{self.question.id}": str(self.answer.id)},
        )

        self.test_review_2 = TestsReviews.objects.create(
            test=self.test,
            user=self.test_user,
            duration=timedelta(minutes=5),
            answers={f"question_{self.question.id}": str(self.answer.id)},
        )


        self.url = reverse("tests:test_group_reviews", args=[self.test.id])
    def test_get_url_status_code_and_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tests/test_group_reviews.html")

    def test_get_context_data(self):
        response = self.client.get(self.url)

        self.assertIn("test", response.context)
        self.assertIn("user_reviews", response.context)

        test = response.context['test']
        user_reviews = response.context['user_reviews']

        self.assertEqual(self.test, test)
        self.assertIn(self.test_review, user_reviews)
        self.assertIn(self.test_review_2, user_reviews)

    def tearDown(self):
        self.test_review_2.delete()
        self.test_review.delete()
        self.answer.delete()
        self.question.delete()
        self.test.delete()
        self.category.delete()
        self.group_membership.delete()
        self.group.delete()
        self.test_user.delete()
        self.user.delete()