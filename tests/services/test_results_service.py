


import base64
from datetime import timedelta
import os
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from tests.models import MatchingPair, Question, TestResult, Tests, TestsReviews


class TestResultsService:

    # get
    @staticmethod
    def get(session, http_request, test_id):
        test = get_object_or_404(Tests.objects.select_related('group'), id=test_id)
        responses = session.get('test_responses', {})
        audio_answers = session.get('autio_answer_', {})
        test_time = session.get('remaining_time', None)

        if test.check_type == Tests.MANUAL_CHECK:
            TestResultsService.save_audio_responses(http_request, responses, audio_answers)
            TestResultsService.clear_test_session(session)

            if not test_time or not responses:
                return 'redirect', reverse_lazy('app:index')
            
            test_duration = timedelta(seconds=test.duration.total_seconds() - test_time)
            TestsReviews.objects.create(
                test=test,
                group=test.group,
                user=http_request.user,
                answers=responses,
                audio_answers=audio_answers,
                duration=test_duration,
            )
            # return render(request, 'tests/success_page_manual_test.html')
            return 'render', None
        else:

            if not test_time:
                return 'redirect', reverse_lazy('app:index')
            
            score, correct_answers, total_questions, test_duration = TestResultsService.calculate_results(test, responses, test_time)
            TestResultsService.save_test_results(http_request, test, score, test_duration)
            TestResultsService.clear_test_session(session)
            context = TestResultsService.get_context_data(test, score, correct_answers, total_questions)
            return 'render', context 
            # (http_request, self.template_name, context)

    @staticmethod
    def save_audio_responses(http_request, responses, audio_answers):
        for key, value in responses.items():
            if 'audio_answer_' in key and value:
                question_id = key.split('audio_answer_')[1]
                audio_data = value.split(',')[1]
                audio_content = base64.b64decode(audio_data)


                filename = f'audio_answer_{question_id}_{http_request.user.id}.wav'
                file_path = os.path.join('answers/audios/', filename)
                audio_file = ContentFile(audio_content, filename)
                saved_file = default_storage.save(file_path, audio_file) 
                file_url = default_storage.url(saved_file)
                audio_answers[question_id] = file_url

                responses[f'audio_answer_{question_id}'] = 'Перенесён'

        http_request.session['audio_answers'] = audio_answers


    @staticmethod
    def calculate_results(test, responses, test_time):
        total_questions = test.questions.count()
        total_points = test.questions.aggregate(Sum('scores'))['scores__sum']
        print('TOTAL POINTS', total_points)
        correct_answers = 0.0
        complete_answers = 0


        for key, value in responses.items():
            if key.startswith('question_'):
                question_id = int(key.split('_')[1])
                question = Question.objects.get(id=question_id)
                complete, correct_answer = TestResultsService.evaluate_question(question, value)
                correct_answers += correct_answer 
                print("ОЧКИ ВОПРОСА", question.scores)
                print("ОЧКИ ответа", int(correct_answers))
                if complete:
                    complete_answers += 1

        
        score = round((correct_answers / total_points) * 100) if total_questions > 0 else 0
        test_duration = timedelta(seconds=test.duration.total_seconds() - test_time)

        return score, int(complete_answers), total_questions, test_duration
    
    @staticmethod
    def evaluate_question(question, value):
        correct_answers = 0.0
        complete_question = False

        if question.question_type == 'MTCH':

            if question.scores_for == Question.SCORE_FOR_ANSWER:
            # questions_count = MatchingPair.objects.filter(question=question).count()

                for left, right in value.items():
                    match = MatchingPair.objects.filter(question=question, left_item=left, right_item=right).first()
                    if match:
                        correct_answers += match.score

                    if correct_answers == question.scores:
                            complete_question = True

            elif question.scores_for == Question.SCORE_FOR_QUESTION:
                matching_pair_dict = {
                    str(left_item): right_item
                    for left_item, right_item in question.matching_pairs.all().values_list('left_item', 'right_item')
                }

                if len(matching_pair_dict) > 0:
                    point = question.scores / len(matching_pair_dict)
                else:
                    # Возвращаем 0 в очках так как правильных ответов 0
                    return complete_question, correct_answers

                for left, right in value.items():
                    if str(left) in matching_pair_dict:
                        
                        expected_right = matching_pair_dict[left]
                        if right == expected_right:
                            correct_answers += point

                if question.scores == correct_answers:
                    complete_question = True

        elif question.answer_type == 'SC':

            if question.scores_for == Question.SCORE_FOR_ANSWER:
                correct_answer = question.answers.filter(is_correct=True).first()
                
                try:
                    if correct_answer and correct_answer.id == int(value):
                        correct_answers += correct_answer.score
                        if correct_answers == question.scores:
                            complete_question = True
                except ValueError as e:
                    print(e)
                
            elif question.scores_for == Question.SCORE_FOR_QUESTION:
                correct_answer = question.answers.filter(is_correct=True).first()

                try:
                    if correct_answer and correct_answer.id == int(value):
                        correct_answers += question.scores
                        complete_question = True
                except ValueError as e:
                    print(e)

                                

        elif question.answer_type == 'MC':
                
                if question.scores_for == Question.SCORE_FOR_ANSWER:
                    correct_answers_dict = {
                        str(answer_id): score    
                        for answer_id, score in question.answers.filter(is_correct=True).values_list('id', 'score')
                    }

                    for v in value:
                        if str(v) in correct_answers_dict:
                            correct_answers += correct_answers_dict[v]

                    if correct_answers == question.scores:
                        complete_question = True

                elif question.scores_for == Question.SCORE_FOR_QUESTION:
                    correct_answers_list = question.answers.filter(is_correct=True).values_list('id', flat=True)

                    if len(correct_answers_list) > 0:
                        points = question.scores / len(correct_answers_list)
                    else:
                        return complete_question, correct_answers

                    try:
                        for v in value:
                            if int(v) in correct_answers_list:
                                correct_answers += points
                    except ValueError as e:
                        print(e)

                    if correct_answers == question.scores:
                        complete_question = True


        elif question.answer_type == 'INP':
            if question.scores_for == Question.SCORE_FOR_ANSWER:
                correct_answers_dict = {
                    str(text).strip().lower(): score
                    for text, score in question.answers.filter(is_correct=True).values_list('text', 'score')
                }
                    
                if correct_answers_dict:
                    lower_value = str(value).strip().lower()
                    if lower_value in correct_answers_dict:

                        correct_answers += correct_answers_dict[lower_value]

                        if correct_answers == question.scores:
                                complete_question = True

            elif question.scores_for == Question.SCORE_FOR_QUESTION:
                correct_answers_list = [
                    str(v).lower().strip() for v in question.answers.filter(is_correct=True).values_list('text', flat=True)
                ]

                if str(value).lower().strip() in correct_answers_list:
                    correct_answers += question.scores
                    complete_question = True



        print("ОТВЕТ", question, correct_answers,":", complete_question)
        return complete_question ,correct_answers
    

    @staticmethod
    def save_test_results(http_request, test, score, test_duration):
        test_result, created = TestResult.objects.get_or_create(
            user=http_request.user,
            test=test,
            group=test.group,
            defaults={'score': score, 'attempts': 1, 'duration': test_duration}
        )

        if not created:
            if test_result.remaining_atemps > 0:
                test_result.attempts += 1
                test_result.duration = test_duration
                test_result.score = max(test_result.score, score)
                test_result.save()


    @staticmethod
    def clear_test_session(session):
        session_keys = ['question_order','question_index','test_responses','remaining_time', 'test_id']
        for key in session_keys:
            if key in session:
                print('DELETE', key)
                del session[key]


    @staticmethod
    def get_context_data(test, score, correct_answers, total_questions):
        return {
            'test': test,
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
        }