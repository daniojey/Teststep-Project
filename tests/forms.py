from datetime import timedelta
from django import forms
from .models import Tests, Question, Answer

class TestForm(forms.ModelForm):
    class Meta:
        model = Tests
        fields = ['name', 'description', 'image', 'duration', 'category']
        widgets = {
            'duration': forms.TimeInput(attrs={'type': 'time'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)  # Извлекаем аргумент 'question'
        super().__init__(*args, **kwargs)
        # Теперь можешь использовать 'question' внутри формы, если нужно

    def clean(self):
        cleaned_data = super().clean()
        duration_minutes = cleaned_data.get('duration_minutes')
        if duration_minutes is not None:
            # Convert minutes to a timedelta
            cleaned_data['duration'] = timedelta(minutes=duration_minutes)
        return cleaned_data

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'image', 'audio']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
