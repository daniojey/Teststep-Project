import random
from django import forms
from .models import Categories, MatchingPair, QuestionGroup, Tests, Question, Answer, TestsReviews

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
    def __init__(self, *args, **kwargs):
        test = kwargs.pop('test', None)  # Забираем тест из kwargs
        super().__init__(*args, **kwargs)

        if test:
            self.fields['group'].queryset = QuestionGroup.objects.filter(test=test)
        else:
            self.fields['group'].queryset = QuestionGroup.objects.none()

    class Meta:
        model = Question
        fields = ['text', 'question_type', 'image', 'audio', 'group']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'question_type': forms.RadioSelect(choices=Question.QUESTION_TYPES),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }

class MatchingPairForm(forms.ModelForm):
    class Meta:
        model = MatchingPair
        fields = ['left_item', 'right_item']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



class TestTakeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Теперь мы передаем только один вопрос
        question = kwargs.pop('question')  # Получаем текущий вопрос
        super().__init__(*args, **kwargs)

        choices = [(a.id, a.text) for a in question.answers.all()]
        random.shuffle(choices)  # Перемешиваем варианты ответа

        # Одиночный выбор (Single Choice)
        if question.question_type == 'SC':
            self.fields[f'answer'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=question.text
            )
        
        # Множественный выбор (Multiple Choice)
        elif question.question_type == 'MC':
            self.fields[f'answer'] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                label=question.text
            )
        
        # Выбор изображения (Image Choice)
        elif question.question_type == 'IMG':
            self.fields[f'answer'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=question.text
            )
        
        # Аудио-вопросы (Audio Answer)
        elif question.question_type == 'AUD':
            # Теперь ключ снова будет содержать ID вопроса
            self.fields[f'audio_answer_{question.id}'] = forms.CharField(
                label=f"{question.text} (Ваш ответ в аудиоформате)",
                widget=forms.HiddenInput(),  # Здесь будет сохраняться URL аудиофайла
                required=False
            )
        
        # Текстовые ответы (Input Answer)
        elif question.question_type == "INP":
            self.fields[f'answer'] = forms.CharField(
                label=f"{question.text}",
                widget=forms.TextInput
            )
        
         # Матчинг (Matching)
        elif question.question_type == 'MTCH':
            left_items = [(pair.left_item, pair.left_item) for pair in question.matching_pairs.all()]
            right_items = [(pair.right_item, pair.right_item) for pair in question.matching_pairs.all()]

            random.shuffle(left_items)
            random.shuffle(right_items)

            for idx, (left_item, _) in enumerate(left_items):
                # Левый элемент просто выводится как текст, без поля ввода
                self.fields[f'matching_left_{idx}'] = forms.CharField(
                    label=left_item,
                    required=False,
                    widget=forms.HiddenInput()  # Прячем реальное поле, но текст останется как label
                )
                
            for idx, (right_item, _) in enumerate(right_items):
                # Правый элемент также выводится как текст, без выпадающего списка
                self.fields[f'matching_right_{idx}'] = forms.CharField(
                    label=right_item,
                    required=False,
                    widget=forms.HiddenInput()  # Прячем поле для выбора
                )


    # def __init__(self, *args, **kwargs):
    #     test = kwargs.pop('test')
    #     super().__init__(*args, **kwargs)
        
    #     questions = list(test.questions.all())
    #     # random.shuffle(questions)

    #     for question in questions:
    #         choices = [(a.id, a.text) for a in question.answers.all()]
    #         random.shuffle(choices)
    #         if question.question_type == 'SC':
    #             self.fields[f'question_{question.id}'] = forms.ChoiceField(
    #                 choices=choices,
    #                 widget=forms.RadioSelect,
    #                 label=question.text
    #             )
    #         elif question.question_type == 'MC':
    #             self.fields[f'question_{question.id}'] = forms.MultipleChoiceField(
    #                 choices=choices,
    #                 widget=forms.CheckboxSelectMultiple,
    #                 label=question.text
    #             )
            
    #         elif question.question_type == 'IMG':
    #             self.fields[f'question_{question.id}'] = forms.ChoiceField(
    #                 choices=choices,
    #                 widget=forms.RadioSelect,
    #                 label=question.text
    #             )
            
    #         elif question.question_type == 'AUD':  # Для аудиовопросов
    #             self.fields[f'audio_answer_{question.id}'] = forms.CharField(
    #                 label=f"{question.text} (Ваш ответ в аудиоформате)",
    #                 widget=forms.HiddenInput(),  # Здесь сохраняется URL до аудио
    #                 required=False
    #             )
            
    #         elif question.question_type == "INP":
    #             self.fields[f'question_{question.id}'] = forms.CharField(
    #                 label=f"{question.text}",
    #                 widget=forms.TextInput,
    #             )

    #         elif question.question_type == 'MTCH':
    #             matching_fields = []
    #             # TODO Реализовать позже


    # def clean(self):
    #     cleaned_data = super().clean()
        
    #     # Создаем копию cleaned_data, чтобы избежать его изменения во время итерации
    #     cleaned_data_copy = cleaned_data.copy()
        
    #     for key, value in cleaned_data_copy.items():
    #         question_id = int(key.split('_')[1])  # Извлекаем ID вопроса
    #         question = Question.objects.get(id=question_id)

    #         # Логика для валидации
    #         if question.question_type == 'SC':
    #             if not value:
    #                 self.add_error(key, "Этот вопрос требует ответа.")
            
    #         # Пример безопасного изменения cleaned_data
    #         # cleaned_data['some_key'] = 'some_value'
        
    #     return cleaned_data
    
 
class TestReviewForm(forms.Form):
    def __init__(self, *args, **kwargs):
        test = kwargs.pop('test')
        answers = kwargs.pop('answers')
        audio_answers = kwargs.pop('audio_answers', {})
        super().__init__(*args, **kwargs)

        questions = test.questions.all()


        for question in questions:

            # Извлекаем ответы пользователя из JSON
            user_answer_ids = answers.get(f'question_{question.id}', [])
            print(user_answer_ids)


            # Получаем правильные ответы
            item = question.answers.filter(is_correct=True)
            ans = [i for i in item]
            result = [i.text for i in ans]
            question_correct = ', '.join(result)


            # Получаем список  по ответам
            try:
                user_answers =[
                    (answer.id, answer.text) for answer in question.answers.filter(id__in=user_answer_ids)
                ]
            except ValueError:
                ...

            # Если одиночный ответ добавляем его вручную в список
            if user_answers == [] and question.question_type == "SC":
                answer = question.answers.filter(id=user_answer_ids)[0]
                user_answers.append((answer.id, answer.text))


            if question.question_type == 'MC':
                self.fields[f'question_{question.id}_approve'] = forms.MultipleChoiceField(
                    label=f"{question.text}: Правильные ответы {question_correct}",
                    choices=user_answers,
                    widget=forms.CheckboxSelectMultiple,
                    required=False,
                    
                )

            elif question.question_type == 'AUD':  # Для вопросов с аудио
                self.fields[f'audio_answer_{question.id}'] = forms.CharField(
                    label=f"Текст вопроса  {question.text}",
                    widget=forms.HiddenInput(),
                    required=False,
                    initial=audio_answers.get(str(question.id))
                )

                self.fields[f"audio_answer_{question.id}_correct"] = forms.BooleanField(
                    label=f"Ответ правильный ?",
                    required=False,
                )

            elif question.question_type == 'INP':
                ans_resp = answers.get(f"question_{question.id}", None)
                item = item[0]
                self.fields[f'question_{question.id}_user_answer'] = forms.CharField(
                    label=f"{question.text}:\nПравильний ответ - {item.text}",
                    widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                    initial=f"Ответ ученика - {ans_resp}",
                    required=False,
                )

                self.fields[f"question_{question.id}_correct"] = forms.BooleanField(
                    label="Ответ верный ?",
                    required=False,
                )

            else:
                self.fields[f'question_{question.id}_approve'] = forms.MultipleChoiceField(
                    label=f"{question.text}: Правльный ответ {question_correct}",
                    choices=user_answers,
                    widget=forms.CheckboxSelectMultiple,
                    required=False,
                )
            
           

                