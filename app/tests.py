from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from tests.models import Tests, TestResult, TestsReviews
from users.models import UsersGroupMembership

# Create your tests here.

User = get_user_model()

class TetsModelTest(TestCase):
    
    def setUp(self) -> None:
        
        self.test = Tests.objects.create(name='testname', )



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