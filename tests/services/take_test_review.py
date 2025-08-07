

from tests.models import Question


class TakeTestReviewService:

    @staticmethod
    def dispatch(session, test, test_student_responses):

        if 'teacher_asnwers' not in session:
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

        