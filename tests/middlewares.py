# middlewares.py
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
            test = get_object_or_404(Tests, id=test_id)
            
        # Если запрос не относится к тесту (например, пользователь покидает страницу)
        def process_response(self, request, response):
            # Проверяем, если пользователь проходит тест и собирается покинуть его
            if 'question_order' in request.session and 'test_id' in request.session:
                test_id = request.session.get('test_id')
                test = get_object_or_404(Tests, id=test_id)

                # Проверяем, если тест не является тестом с ручной проверкой
                if test.check_type != Tests.MANUAL_CHECK:
                    # Если запрос не относится к тесту (например, пользователь покидает страницу)
                    if not request.path.startswith(reverse('tests:take_test', kwargs={'test_id': test_id})):
                        # Сохраняем результат с 0 баллов для автоматических тестов
                        if request.user.is_authenticated:
                            TestResult.objects.create(
                                user=request.user,
                                test=test,
                                score=0  # Результат 0 баллов
                        )
                            
                        # Очищаем сессию для этого теста
                        if 'test_id' in request.session:
                            del request.session['test_id']
                        if 'question_order' in request.session:
                            del request.session['question_order']
                        if 'question_index' in request.session:
                            del request.session['question_index']
                        if 'test_responses' in request.session:
                            del request.session['test_responses']
                        if 'remaining_time' in request.session:
                            del request.session['remaining_time']

        return response