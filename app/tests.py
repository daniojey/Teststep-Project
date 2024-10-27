from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from tests.models import Categories, Tests, TestResult, TestsReviews
from users.models import UsersGroup, UsersGroupMembership

# Create your tests here.

User = get_user_model()

class IndexViewTest(TestCase):
    
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

        self.test_review = Tests.objects.create(
            user=self.user,
            name='Second Test',
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

        self.review_test = TestsReviews.objects.create(
            test=self.test_review,
            user=self.user,
            duration=timedelta(seconds=30),
            group='test_group',
            score=50,
            answers={'question_1':'1'}
        )

    def test_index_view_status_code(self):
        response = self.client.get(reverse('app:index'))
        self.assertEqual(response.status_code, 200)

    def test_index_view_redirects_for_unauthenticated(self):
        # Выходим из учетной записи перед запросом
        self.client.logout()

        # Отправляем запрос к представлению
        index_url = reverse('app:index')
        response = self.client.get(index_url)

        # Ожидаемый URL перенаправления
        expected_url = f"{reverse('users:login')}?next={index_url}"
        
        # Проверка перенаправления
        self.assertRedirects(response, expected_url)

    def test_index_view_template_user(self):
        response = self.client.get(reverse('app:index'))
        self.assertTemplateUsed(response, 'app/index.html')

    def test_index_view_context_data(self):
        response = self.client.get(reverse('app:index'))
         # Проверка контекста
        self.assertIn('tests', response.context)
        self.assertIn('uncompleted_tests', response.context)
        self.assertIn('awaiting_tests', response.context)
        self.assertIn('completed_tests', response.context)
        self.assertIn('group', response.context)

        # Проверка, что HTML-контент соответствует ожиданиям, добавьте здесь точные строки
        self.assertIn('Очікують на перевірку', response.content.decode('utf-8'))
        self.assertIn('Невиконані тести', response.content.decode('utf-8'))
        self.assertIn('Пройдені тести', response.content.decode('utf-8'))

        completed_tests = response.context['completed_tests']
        awaiting_tests = response.context['awaiting_tests']
        uncompleted_tests = response.context['uncompleted_tests']

        # # Проверка значений
        self.assertIn(self.test, completed_tests)
        self.assertIn(self.test_review, awaiting_tests)
        self.assertIn(self.test_uncompleted, uncompleted_tests)

    def tearDown(self) -> None:
        if self.test.pk:
            self.test.delete()
        # self.category.delete()
        # self.group_membeship.delete()
        # self.group.delete()
        # self.user.delete()
        # self.test_result.delete()
        # self.test_review.delete()

# class IndexViewTest(TestCase):
#     def setUp(self) -> None:
#         # Создаём пользователя
#         self.user = User.objects.create(username='testuser', password='password123')
#         self.client.login(username='testuser', password='password123')

#         # Создаём тест, тестовые результаты и ревью для пользователя
#         self.test = Tests.objects.create(name='Sample test')
#         self.completed_test = TestResult.objects.create(user=self.user, test=self.test, score=0)
#         self.awaiting_test_review = TestsReviews.objects.create(user=self.user, test=self.test, answers={})

#         # Создаём группу и добавляем пользователя в неё 
#         self.group = UsersGroupMembership.objects.create(user=self.user, group='Test Group')

#     def test_index_view_context_data(self):
#         # Выполняем GET-запрос к IndexView
#         response = self.client.get(reverse('app:index'))

#         # Проверяем статус пользователя
#         self.assertEqual(response.status_code, 200)

#         # Проверка данныз контекста
#         context = response.context

#         # Вроверка данных контекста
#         context = response.context
#         self.assertIn('tests', context)
#         self.assertIn('uncompleted_tests', context)
#         self.assertIn('awaiting_tests', context)
#         self.assertIn('completed_tests', context)
#         self.assertIn('group', context)

#         # Проверка что группа пользователя отображается 
#         self.assertEqual(context['group'], 'TestGroup')

#         self.assertEqual(
#             response.context['completed_tests'].first().name, "Sample test"
#         )
#         self.assertEqual(
#             response.context['completed_tests'].first().score, 0
#         )
#         self.assertEqual(
#             response.context['completed_tests'].first().user, self.user
#         )   

#         # Проверка списка завершенных и ожидающих проверку тестов
#         completed_tests = context['completed_tests']
#         awaiting_tests = context['awaiting_tests']

#         # Убеждаемс что нужный тест отображается в завершенных
#         self.assertIn(self.completed_test.test_id, completed_tests.values_list('id', flat=True))

#         # Убежлаемся что тест ожидающий проверки в соотвецтвующем списке
#         self.assertIn(self.awaiting_test_review.test_id, awaiting_tests.values_list('id', flat=True))