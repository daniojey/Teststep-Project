import random
from django import forms
from .models import Categories, QuestionGroup, Tests, Question, Answer, TestsReviews

class TestForm(forms.ModelForm):
    class Meta:
        model = Tests
        fields = ['name', 'description', 'image', 'duration', 'category', 'check_type']
        widgets = {
            'duration': forms.TimeInput(attrs={'type': 'time'}, format="%M:%S"),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)  # Извлекаем аргумент 'question'
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Получаем первую категорию из набора
        first_category = Categories.objects.first()
        if first_category:
            self.fields['category'].initial = first_category

       
    def save(self, commit=True):
        test = super().save(commit=False)
        if self.user:
            test.user = self.user
        if commit:
            test.save()
        return test
    
class QuestionGroupForm(forms.ModelForm):
    class Meta:
        model = QuestionGroup
        fields = ['name']

class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['text', 'question_type', 'image', 'audio', 'group']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'question_type': forms.RadioSelect(choices=Question.QUESTION_TYPES),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }
        
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
        }

        is_correct = forms.CheckboxSelectMultiple()


class TestTakeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        test = kwargs.pop('test')
        super().__init__(*args, **kwargs)
        
        questions = list(test.questions.all())
        random.shuffle(questions)

        for question in questions:
            choices = [(a.id, a.text) for a in question.answers.all()]
            random.shuffle(choices)
            if question.question_type == 'SC':
                self.fields[f'question_{question.id}'] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.RadioSelect,
                    label=question.text
                )
            elif question.question_type == 'MC':
                self.fields[f'question_{question.id}'] = forms.MultipleChoiceField(
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple,
                    label=question.text
                )
            
            elif question.question_type == 'IMG':
                self.fields[f'question_{question.id}'] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.RadioSelect,
                    label=question.text
                )
            
            elif question.question_type == 'AUD':
                 self.fields[f'question_{question.id}'] = forms.CharField(
                    widget=forms.HiddenInput(),
                    required=False
                )

            elif question.question_type == 'MTCH':
                matching_fields = []
                # Реализовать позже


    def clean(self):
        cleaned_data = super().clean()
        
        # Создаем копию cleaned_data, чтобы избежать его изменения во время итерации
        cleaned_data_copy = cleaned_data.copy()
        
        for key, value in cleaned_data_copy.items():
            question_id = int(key.split('_')[1])  # Извлекаем ID вопроса
            question = Question.objects.get(id=question_id)

            # Логика для валидации
            if question.question_type == 'SC':
                if not value:
                    self.add_error(key, "Этот вопрос требует ответа.")
            
            # Пример безопасного изменения cleaned_data
            # cleaned_data['some_key'] = 'some_value'
        
        return cleaned_data
    
 
class TestReviewForm(forms.Form):
    def __init__(self, *args, **kwargs):
        test = kwargs.pop('test')
        answers = kwargs.pop('answers')
        super().__init__(*args, **kwargs)

        questions = test.questions.all()



        for question in questions:

            # Извлекаем ответы пользователя из JSON
            user_answer_ids = answers.get(f'question_{question.id}', [])


            # Получаем правильные ответы
            item = question.answers.filter(is_correct=True)
            ans = [i for i in item]
            result = [i.text for i in ans]
            question_correct = ', '.join(result)

            # Получаем список  по ответам
            user_answers =[
                (answer.id, answer.text) for answer in question.answers.filter(id__in=user_answer_ids)
            ]

            # Если одиночный ответ добавляем его вручную в список
            if user_answers == []:
                answer = question.answers.filter(id=user_answer_ids)[0]
                user_answers.append((answer.id, answer.text))


            if question.question_type == 'MC':
                self.fields[f'question_{question.id}_approve'] = forms.MultipleChoiceField(
                    label=f"{question.text}: Правильные ответы {question_correct}",
                    choices=user_answers,
                    widget=forms.CheckboxSelectMultiple,
                    required=False,
                    
                )

            else:
                self.fields[f'question_{question.id}_approve'] = forms.MultipleChoiceField(
                    label=f"{question.text}: Правльный ответ {question_correct}",
                    choices=user_answers,
                    widget=forms.CheckboxSelectMultiple,
                    required=False,
                )



                