from django import forms
from .models import Tests, Question, Answer

class TestForm(forms.ModelForm):
    class Meta:
        model = Tests
        fields = ['name', 'description', 'image', 'duration', 'category']
        widgets = {
            'duration': forms.TimeInput(attrs={'type': 'time'}, format="%M:%S"),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)  # Извлекаем аргумент 'question'
        super().__init__(*args, **kwargs)
        # Теперь можешь использовать 'question' внутри формы, если нужно

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
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TestTakeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        test = kwargs.pop('test')
        super().__init__(*args, **kwargs)
        
        questions = test.questions.all()
        for question in questions:
            choices = [(a.id, a.text) for a in question.answers.all()]
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
        return cleaned_data