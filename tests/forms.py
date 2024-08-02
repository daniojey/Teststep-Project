from django import forms
from .models import Tests, Question, Answer

class TestForm(forms.ModelForm):
    class Meta:
        model = Tests
        fields = ['name', 'description', 'image', 'duration']
        widgets = {
            'duration': forms.TimeInput(attrs={'type': 'time'})  # Опционально: можно настроить отображение времени
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'image', 'audio']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
