# middlewares.py
from datetime import timedelta
import re
from django.shortcuts import get_object_or_404
from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from .models import Tests, TestResult

class TestExitMiddleware(MiddlewareMixin):
    """
    Middleware для обработки выхода пользователя из теста и сохранения результата с нулевым баллом.
    """

    def process_response(self, request, response):
        # Проверяем, если пользователь проходит тест и собирается покинуть его
        if 'question_order' in request.session and 'test_id' in request.session:
            test_id = request.session.get('test_id')
            # print(f"АЙДИ ТЕСТА В СЕССИИ - {test_id}")
            test = get_object_or_404(Tests, id=test_id)

            # Проверяем, если тест не является тестом с ручной проверкой
            if test.check_type != Tests.MANUAL_CHECK:
                # Если запрос не относится к текущему тесту
                current_test_path = reverse('tests:take_test', kwargs={'test_id': test_id})
                # print('ПУть request', request.path)
                # print(current_test_path)
                if not self.is_test_path(request.path, current_test_path):
                    print('НЕВЕРНЫЙ ПУТЬ', request.path)
                    # Сохраняем резулттат с 0 баллов для автоматического теста 
                    if request.user.is_authenticated:
                        TestResult.objects.get_or_create(
                            user=request.user,
                            test=test,
                            score=0,
                            attempts=2,
                            duration=timedelta(hours=0, minutes=0,seconds=0)
                        )
                    
                        self.clear_test_session(request)

        return response

    def is_test_path(self, request_path, test_path):
        """
        Проверяет, начинается ли путь запроса с пути теста.
        Исключает пути к медиафайлам, статическим файлам и другим не связанным с тестом запросам.
        """
        # Список исключений (путь к медиафайлам, статике, csp-report и другие)
        excluded_paths = [
            '/media/',  # Путь к медиафайлам
            '/static/',  # Путь к статическим файлам
            '/csp-report/',  # Путь для отчётов CSP
            '/favicon.ico',  # Иконка сайта
            '/robots.txt',  # Файл robots.txt
            '/admin/',
            '/.well-known/',
        ]
        
        # Проверяем, если путь запроса совпадает с исключениями
        if any(request_path.startswith(excluded) for excluded in excluded_paths):
            return True

        # Проверка на путь текущего теста
        res = bool(re.match(f"^{re.escape(test_path)}", request_path))
        return res

    def clear_test_session(self, request):
        """Очищает данные теста из сессии."""
        # print('ОЧИСТКА СЕССИИ В MIDDLEWARE')
        keys_to_clear = ['test_id', 'question_order', 'question_index', 'test_responses', 'remaining_time', 'test_start_time']
        for key in keys_to_clear:
            if key in request.session:
                del request.session[key]