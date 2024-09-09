from tests.models import Answer


class MultypleChoiceStrategy:
    def calculate_point(self, question, selected_ids, correct_answer, form):
        correct_answer_ids = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
        

        for i in correct_answer_ids:
            a = Answer.objects.filter(id=i)
            # print(a)

        # print(correct_answer)
        # print(correct_answer_ids)