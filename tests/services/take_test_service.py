

from datetime import datetime
import random
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import localtime, now

from tests.models import MatchingPair, Question, QuestionGroup


class TakeTestService:

    # dispatch методы
    @staticmethod
    def check_session_test(test, session, http_response):
        r, url = TakeTestService.check_aviability_test(test, session, http_response)

        match r:
            case 'redirect':
                return 'redirect', url
            
        
        session_test_id = session.get('test_id')
        if test.id != session_test_id and session_test_id != None:
            TakeTestService.clear_test_session(session=session)

        session['test_id'] = test.id


        if 'test_start_time' not in session:
            session['test_start_time'] = now().timestamp()

        if 'remaining_time' not in session:
            session['remaining_time'] = test.duration.total_seconds()

        if 'question_order' not in session:
            response, url = TakeTestService.initialize_test_session(session, test, http_request=http_response)
            if response == 'redirect':
                return 'redirect', url
        
        return 'success', None

    
    @staticmethod
    def check_aviability_test(test, session, http_response):
        server_time = timezone.make_aware(datetime.now(), timezone.get_default_timezone())

        if server_time < localtime(test.date_in) or server_time > localtime(test.date_out):
            if 'test_responses' in session:

                if len(session.get('test_responses')) != 0:
                    return 'redirect', reverse_lazy('tests:test_results', kwarkg={'test_id':test.id})
                else:
                    TakeTestService.clear_test_session(session)
                    return 'redirect', reverse_lazy('app:index')
                
            else:
                return 'redirect', reverse_lazy('app:index')
        else:
            return 'None', None


    @staticmethod
    def clear_test_session(session):
        # Очищаем все возможные ключи из сессии
        keys_to_clear = ['test_id', 'question_order', 'question_index', 'test_responses', 'remaining_time', 'test_start_time']
        for key in keys_to_clear:
            if key in session:
                del session[key]


    @staticmethod
    def initialize_test_session(session, test, http_request):
        questions_by_group = {}

        # Проходим по группе вопросов и все вопросы для каждой из них после сохраняем в виде словаря Группа:[Вопросы]
        for group in QuestionGroup.objects.filter(test=test).prefetch_related('questions_group'):
            questions_by_group[group.name] = list(group.questions_group.all())

        # Проходим по словарю questions_by_group и перемещиваем все вопросы для каждой группы
        for group_name, questions in questions_by_group.items():
            random.shuffle(questions)

        # Обединяем все перемешанные вопросы в один список
        all_questions = []
        for questions in questions_by_group.values():
            all_questions.extend(questions)

        # Выбираем оставшиеся вопросы которые не предналежат ни одной из групп после чего перемешиваем их и добавляем в список
        questions_not_group = list(Question.objects.filter(test=test, group=None))
        random.shuffle(questions_not_group)
        all_questions.extend(questions_not_group)

        if len(all_questions) == 0:
            # Если нет вопросов, то очищаем сессию и перенаправляем на главную страницу
            TakeTestService.clear_test_session(request=http_request)
            return 'redirect', reverse_lazy('app:index')
        else:
            # Иначе инициализируем начальные данные для прохождения теста
            session['question_order'] = [q.id for q in all_questions]
            session['question_index'] = 0  # Начинаем с первого вопроса
            session['test_responses'] = {}  # Для хранения ответов

        return 'success', None


    # form_valid
    @staticmethod
    def form_valid(form, session, http_request, current_question):
        is_mobile = http_request.user_agent.is_mobile
        answer = form.cleaned_data.get('answer')

        if current_question.question_type == 'AUD' or current_question.question_type == 'IMG' or current_question.question_type == 'TXT':
            if current_question.answer_type == 'AUD':
                audio_answer = form.cleaned_data.get(f'audio_answer_{current_question.id}', None)
                if audio_answer is not None:
                    session['test_responses'][f"audio_answer_{current_question.id}"] = audio_answer
            else:
                if answer:
                    session['test_responses'][f"question_{current_question.id}"] = answer

        elif current_question.question_type == 'MTCH':
            responses = http_request.POST
            dict_items = {}

            if is_mobile:
                for left, right in responses.items():
                    if left.startswith('matching_left'):
                        truncate_string = left.replace('matching_left_', '').split('_')
                        left_item = truncate_string[1]
                        try:
                            right_item = MatchingPair.objects.get(id=right).right_item
                        except ValueError:
                            continue

                        # print('Данные', left_item,'-', right_item)
                        dict_items[left_item] = right_item

                session['test_responses'][f"question_{current_question.id}_type_matching"] = dict_items
            else:

                for left, right in responses.items():
                    if left.startswith('answer_'):
                        left_item = left.split('answer_')[1]
                        dict_items[left_item] = right
                session['test_responses'][f"question_{current_question.id}_type_matching"] = dict_items
        else:
            if answer:
                session['test_responses'][f"question_{current_question.id}"] = answer

        remaining_time = int(http_request.POST.get('remaining_time', 0))
        session['remaining_time'] = remaining_time

        session['question_index'] += 1

        question_order = session['question_order']
        question_index = session['question_index']
        test_id = session.get('test_id')
        if question_index >= len(question_order):
            return 'results',  reverse_lazy('tests:test_results', kwargs={'test_id': test_id})

        return 'continue', reverse_lazy('tests:take_test', kwargs={'test_id': test_id})