import random
from django import forms
from .models import Categories, Tests, Question, Answer, TestsReviews

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

class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ['text', 'question_type', 'image', 'audio']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'question_type': forms.RadioSelect(choices=Question.QUESTION_TYPES),
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
                self.fields[f'question_{question.id}'] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.RadioSelect,
                    label=question.text
                )

            elif question.question_type == 'MTCH':
                matching_fields = []
                # Реализовать позже



    def clean(self):
        cleaned_data = super().clean()
        for key, value in cleaned_data.items():
            if key.startswith('question_'):
                question_id = int(key.split('_')[1])
                question = Question.objects.get(id=question_id)
                
                if question.question_type == 'SC':
                    if not value:
                        self.add_error(key, "Выберите один из вариантов.")
                elif question.question_type == 'MC':
                    if not value:
                        self.add_error(key, "Выберите хотя бы один из вариантов.")
                elif question.question_type == 'MTCH':
                # Проверка ответа для matching
                    if len(value) != len(question.answers.all()):
                        self.add_error(key, "Соответствия не установлены корректно.")
                
                # Проверка на соответствие ключ-значение
                    for left, right in value.items():
                        if not question.answers.filter(text=left, matching_answer=right).exists():
                             self.add_error(key, "Некорректное соответствие для {}.".format(left))

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

            # Приводим одиночный ответ к списку
            if isinstance(user_answer_ids, str):  # Если ответ одиночный, он представлен как строка
                user_answer_ids = [user_answer_ids]
            
            # Преобразуем строки с id в числа, если нужно
            user_answer_ids = [int(ans_id) for ans_id in user_answer_ids]
            
            # Формируем текст выбранного ответа
            selected_answers_text = ', '.join(
                answer.text for answer in question.answers.filter(id__in=user_answer_ids)
            )

            # Поле с текстом вопроса
            self.fields[f'question_{question.id}_text'] = forms.CharField(
                initial=question.text,
                label=question.text,
                required=False,
                widget=forms.TextInput(attrs={'readonly': 'readonly'})
            )

            # Поле с ответом пользователя
            self.fields[f'question_{question.id}_selected_answer'] = forms.CharField(
                initial=selected_answers_text,
                label='Ответ ученика',
                required=False,
                widget=forms.TextInput(attrs={'readonly': 'readonly'})
            )

            # Поле для учителя, чтобы отметить правильность ответа
            self.fields[f'question_{question.id}_approved'] = forms.BooleanField(
                label="Верно?",
                required=False
            )