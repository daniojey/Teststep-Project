

import json
from django.urls import reverse_lazy
from tests.models import Question


class TakeTestReviewService:

    @staticmethod
    def dispatch(session, test, test_student_responses):

        if 'teacher_answers' not in session:
            print('ОБНОВЛЕНИЕ очков')
            session['teacher_answers'] = 0.0

        required_keys = ['teacher_answers', 'test_review_session', 'question_index', 'teacher_responses', 'test_student_responses_id']
        
        missing_keys = [key for key in required_keys if key not in session]
        
        if missing_keys:
            TakeTestReviewService.initialize_session_test(
                session=session,
                test=test,
                test_student_responses=test_student_responses,
            )


    @staticmethod
    def initialize_session_test(session, test, test_student_responses):
        questions = Question.objects.filter(test=test)

        if len(questions) == 0:
            session['test_review_session'] = []
        else:
            session['test_review_session'] = [q.id for q in questions]

        session['question_index'] = 0
        session['teacher_responses'] = {}
        # self.request.session['correct_answers'] = 0.0
        session['test_student_responses_id'] = test_student_responses.id

    
    @staticmethod
    def get_form_kwargs(session, test_student_responses):
        question_order = session['test_review_session']
        question = session['question_index']
        
        current_question_id = question_order[question]

        try:
            current_question = Question.objects.select_related('group').prefetch_related('matching_pairs','answers').get(id=current_question_id)
        except Question.DoesNotExist:
            return 'Not_found'
        
        if current_question.answer_type == 'AUD':
            current_students_question = test_student_responses.audio_answers.get(f'audio_answer_{current_question_id}', [])
        elif current_question.question_type == 'MTCH':
            current_students_question = test_student_responses.answers.get(f'question_{current_question_id}_type_matching', [])
        else:
            current_students_question = test_student_responses.answers.get(f'question_{current_question_id}', [])

        return {
            "student_question": current_students_question,
            "question": current_question,
            "audio_answer": test_student_responses.audio_answers, 
        }
    
    @staticmethod
    def form_valid(action, session, current_question, http_request, form):

        if action == 'correct':
                session['teacher_answers'] += float(current_question.scores)
        elif action == 'incorrect':
            pass

        elif action == 'partial':
                print(http_request.POST)

                if current_question.question_type == 'MTCH':
                    if current_question.scores_for == Question.SCORE_FOR_ANSWER:
                        matching_pairs_dict = {
                            str(pair.left_item): pair.score
                            for pair in current_question.matching_pairs.all()
                        }

                        print(matching_pairs_dict)
                        matching_pairs =  {
                            left: right
                            for left, right in current_question.matching_pairs.all().values_list('left_item', 'right_item')
                        }

                        print(matching_pairs)

                        for key, value in http_request.POST.items():
                            if key.startswith('answer_'):
                                # Получаем наш левый и правый ответ
                                left_item = key.replace('answer_', '')
                                right_item = value

                                # Проверяем наличие в словаре ответов
                                if left_item in matching_pairs:
                                    
                                    # Если елемент найден то также проверяем что right совпадает если так то засчитываем балл
                                    expect_right = matching_pairs[left_item]
                                    if right_item == expect_right:
                                        session['teacher_answers'] += matching_pairs_dict[left_item]

                    elif current_question.scores_for == Question.SCORE_FOR_QUESTION:
                        matching_pairs_dict =  {
                            str(left): right
                            for left, right in current_question.matching_pairs.all().values_list('left_item', 'right_item')
                        }

                        if len(matching_pairs_dict) > 0:
                            point = current_question.scores / len(matching_pairs_dict)
                        else:
                            point = 0

                        for key, value in http_request.POST.items():
                            if key.startswith('answer_'):
                                # Получаем наш левый и правый ответ
                                left_item = key.replace('answer_', '')
                                right_item = value

                                if left_item in matching_pairs_dict:
                                    expect_right = matching_pairs_dict[left_item]
                                    if right_item == expect_right:
                                        session['teacher_answers'] += point


                elif current_question.answer_type == 'SC':
                    if current_question.scores_for == Question.SCORE_FOR_ANSWER:
                        answer_dict = {
                            str(ids): score
                            for ids, score in current_question.answers.filter(is_correct=True).values_list('id', 'score')
                        }

                        # answer = list(self.current_question.answers.filter(is_correct=True).values_list('id', flat=True))
                        
                        student_answer = form.cleaned_data.get('answer')

                        if str(student_answer) in answer_dict:
                            print(answer_dict[student_answer])
                            session['teacher_answers'] += answer_dict[student_answer]

                    elif current_question.scores_for == Question.SCORE_FOR_QUESTION:
                        answer = current_question.answers.filter(is_correct=True).values_list('id', flat=True)
                        print(answer)

                        student_answer = form.cleaned_data.get('answer')

                        try:
                            if int(student_answer) in answer:
                                session['teacher_answers'] += current_question.scores
                        except ValueError as e:
                            print(e)


                elif current_question.answer_type == 'MC':
                    if current_question.scores_for == Question.SCORE_FOR_ANSWER:
                        answers_test_dict = {
                            str(ids): score 
                            for ids, score in  current_question.answers.filter(is_correct=True).values_list('id', 'score')
                        }
                        
                        students_answers = form.cleaned_data.get('answer')

                        for answer in students_answers:
                            if str(answer) in answers_test_dict:
                                print(answers_test_dict[answer])
                                session['teacher_answers'] += answers_test_dict[answer]

                    elif current_question.scores_for == Question.SCORE_FOR_QUESTION:
                        answers_tuple = tuple(current_question.answers.filter(is_correct=True).values_list('id', flat=True))
                        
                        # answers_list = self.current_question.answers.filter(is_correct=True).values_list('id', flat=True)

                        if len(answers_tuple) > 0:
                            point = current_question.scores / len(answers_tuple)
                        else:
                            point = 0

                        students_answers = form.cleaned_data.get('answer')

                        for answer in students_answers:
                            try:
                                if int(answer) in answers_tuple:
                                    http_request.session['teacher_answers'] += point
                            except ValueError as e:
                                print(e)
                                continue


                elif current_question.answer_type == 'INP':
                    if current_question.scores_for == Question.SCORE_FOR_ANSWER:
                        answers_dict = {
                            str(text).lower().strip(): score
                            for text, score in  current_question.answers.filter(is_correct=True).values_list('text', 'score')
                        }

                        get_student_answer = form.cleaned_data.get('answer', '')

                        if isinstance(get_student_answer, str):
                            student_answer = get_student_answer.lower().strip()
                        else:
                            student_answer = ''

                        if student_answer in answers_dict:
                            print(answers_dict[student_answer])
                            session['teacher_answers'] += answers_dict[student_answer]
                        else:
                            session['teacher_answers'] += current_question.scores / 2

                    elif current_question.scores_for == Question.SCORE_FOR_QUESTION:
                        answers_tuple = tuple(
                            str(text).lower().strip() for text in current_question.answers.filter(is_correct=True).values_list('text', flat=True))
                        
                        get_student_answer = str(form.cleaned_data.get('answer')).lower().strip()

                        if isinstance(get_student_answer, str):
                            student_answer = get_student_answer.lower().strip()
                        else:
                            student_answer = ''

                        if student_answer in answers_tuple:
                            session['teacher_answers'] += current_question.scores
                                       
                                       
                elif current_question.answer_type == 'AUD':
                    session['teacher_answers'] += current_question.scores / 2

        print(session['teacher_answers'], '/', current_question.scores)
        if session['question_index'] + 1 < len(session['test_review_session']):
            session['question_index'] += 1
            return 'success', None
        else:
            return 'redirect', reverse_lazy('tests:test_review_results')
        
    
    @staticmethod
    def get_current_answers(current_question, is_mobile):

        if current_question.question_type == Question.MATCHING:
            # current_answers = self.current_question.matching_pairs.all()
            current_answers = json.dumps({
                str(pair.left_item): pair.right_item
                for pair in current_question.matching_pairs.all()
            })
        else:

            if is_mobile:
                current_answers = [answer.text for answer in current_question.answers.filter(is_correct=True)]
            else:
                current_answers = json.dumps({
                    str(answer.id): answer.text
                    
                    for answer in current_question.answers.filter(is_correct=True)
                })

        return current_answers