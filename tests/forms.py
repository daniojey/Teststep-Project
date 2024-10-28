from cProfile import label
import random
import json
from django import forms

from users.models import User, UsersGroupMembership
from .models import Categories, MatchingPair, QuestionGroup, Tests, Question, Answer, TestsReviews

class TestForm(forms.ModelForm):
    class Meta:
        model = Tests
        fields = ['name', 'description', 'image', 'duration','category', 'check_type', 'date_out']
        widgets = {
            'duration': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Введіть тривалісь тесту гг:хх:сс)',
                'pattern': '^([0-9]{1,2}):([0-5][0-9]):([0-5][0-9])$',  # Опционально для валидации в браузере
                'title': 'формат гг:хх:сс'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'date_out': forms.DateInput(attrs={'type': 'date'}),
        }


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Получаем группу, в которой состоит пользователь
        user_group = UsersGroupMembership.objects.filter(user=self.user).first()
        if user_group:
            # Получаем всех пользователей группы
            users_in_group = UsersGroupMembership.objects.filter(group=user_group.group)
            choices_user = [(user.user.id, user.user.username) for user in users_in_group]
            
            # Добавляем поле students с выбором
            self.fields['students'] = forms.MultipleChoiceField(
                choices=choices_user,
                widget=forms.CheckboxSelectMultiple,
                label="Оберіть студентів"
            )


    # def clean(self):
    #     cleaned_data = super().clean()
    #     print(f"Cleaned data: {cleaned_data}")  # Выводим содержимое cleaned_data
        
    #     selected_students = cleaned_data.get('students', [])
    #     print(f"Selected students: {selected_students}")  # Проверяем выбранных студентов

    #     # Проверяем, что есть выбранные студенты
    #     if not selected_students or not isinstance(selected_students, (list, tuple)):
    #         raise forms.ValidationError("Не выбраны студенты.")

    #     # Получаем только ID студентов
    #     selected_students_ids = [str(student.id) for student in selected_students]
    #     print(f"Selected students IDs: {selected_students_ids}")  # Отладка

    #     # Сохраняем выбранные студенты в cleaned_data
    #     cleaned_data['students'] = selected_students_ids  # Храним ID студентов как список строк
    #     return cleaned_data



class TestsAdminForm(forms.ModelForm):
    class Meta:
        model = Tests
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    
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

class QuestionStudentsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        test = kwargs.pop('test', None)  # Текущий тест
        user = kwargs.pop('user', None)  # Текущий пользователь (учитель)
        super().__init__(*args, **kwargs)


         # Получаем группу, в которой состоит учитель
        user_group = UsersGroupMembership.objects.filter(user=user).first()
        if user_group:
            students_in_group = UsersGroupMembership.objects.filter(group=user_group.group)

            # Список студентов для чекбоксов
            students = [(item.user.id, item.user.username) for item in students_in_group]

            # Заполняем поле с чекбоксами
            self.fields['students'] = forms.MultipleChoiceField(
                choices=students,  # Список студентов в формате (id, имя)
                widget=forms.CheckboxSelectMultiple,
                label='Студенти',
                required=False
            )
        

        # Устанавливаем начальные значения для чекбоксов, если студенты уже выбраны
        if test and test.students:
            try:
                self.initial['students'] = [str(student_id) for student_id in test.students['students']]  # JSONField хранит список ID
            except Exception as e:
                print(f"У вашій группі на данний момент відсутні студенти {e}")

    def clean_students(self):
        students = self.cleaned_data.get('students')
        print(students)
        return students  # Убедитесь, что возвращаете список


    class Meta:
        model = Tests
        fields = ['students']

    
    # def clean_data(self):
    #     students = self.cleaned_data.get('students', [])

    #     # Проверяем, что все выбранные студенты существуют в базе данных
    #     for student in students:
    #         if not User.objects.filter(id=student.id).exists():
    #             raise forms.ValidationError(f"Пользователь {student} не существует.")
        
    #     return students


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
           self.fields[f'answer'] = forms.CharField(
                label=f"{question.text}",
                widget=forms.TextInput
            )
        
        # Аудио-вопросы (Audio Answer)
        elif question.question_type == 'AUD':
            self.fields[f'answer'] = forms.CharField(
                label=f"{question.text}",
                widget=forms.TextInput
            )
            # # Теперь ключ снова будет содержать ID вопроса
            # self.fields[f'audio_answer_{question.id}'] = forms.CharField(
            #     label=f"{question.text} (Ваша відповідь в аудіо)",
            #     widget=forms.HiddenInput(),  # Здесь будет сохраняться URL аудиофайла
            #     required=False
            # )
        
        # Текстовые ответы (Input Answer)
        elif question.question_type == "INP":
            self.fields[f'answer'] = forms.CharField(
                label=f"{question.text}",
                widget=forms.TextInput
            )
        
         # Матчинг (Matching)
        elif question.question_type == 'MTCH':
            left_items = [pair.left_item for pair in question.matching_pairs.all()]
            right_items = [pair.right_item for pair in question.matching_pairs.all()]

            random.shuffle(left_items)
            random.shuffle(right_items)
            

            for i , pair in enumerate(question.matching_pairs.all()):
                # Левый элемент просто выводится как текст
                self.fields[f'matching_left_{pair.id}'] = forms.CharField(
                    label=left_items[i],
                    required=False,
                    widget=forms.HiddenInput()  # Прячем реальное поле, но текст останется как label
                )

                # Правый элемент также выводится как текст
                self.fields[f'matching_right_{pair.id}'] = forms.CharField(
                    label=right_items[i],
                    required=False,
                    widget=forms.HiddenInput()  # Прячем поле для выбора
                )



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
                    label=f"{question.text}: Правильні відвопіді {question_correct}",
                    choices=user_answers,
                    widget=forms.CheckboxSelectMultiple,
                    required=False,
                    
                )

            elif question.question_type == 'AUD':  # Для вопросов с аудио
                self.fields[f'audio_answer_{question.id}'] = forms.CharField(
                    label=f"Текст питання  {question.text}",
                    widget=forms.HiddenInput(),
                    required=False,
                    initial=audio_answers.get(str(question.id))
                )

                self.fields[f"audio_answer_{question.id}_correct"] = forms.BooleanField(
                    label=f"Відповідь вірна ?",
                    required=False,
                )

            elif question.question_type == 'INP':
                ans_resp = answers.get(f"question_{question.id}", None)
                item = item[0]
                self.fields[f'question_{question.id}_user_answer'] = forms.CharField(
                    label=f"{question.text}:\nВірна відповідь ? - {item.text}",
                    widget=forms.Textarea(attrs={'readonly': 'readonly'}),
                    initial=f"Відповідь студента - {ans_resp}",
                    required=False,
                )

                self.fields[f"question_{question.id}_correct"] = forms.BooleanField(
                    label="Відповідь вірна ?",
                    required=False,
                )
            elif question.question_type == 'MTCH':
                answers_mtch = [f"{item.left_item}-{item.right_item}|" for item in MatchingPair.objects.filter(question=question)]
                user_answers = answers.get(f"question_{question.id}_type_matching", None)
                answer_choise = [(i, f"{key}-{value}") for i, (key, value) in enumerate(user_answers.items())]
                answers_mtch = " ".join(answers_mtch)

                self.fields[f'question_{question.id}_MT'] = forms.CharField(
                    label=f"{question.text}:\nВірна відповідь ? ",
                    widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                    initial=answers_mtch,
                    required=False,
                )

                self.fields[f"question_{question.id}_mtch"] = forms.MultipleChoiceField(
                    label='Відповіді студента',
                    choices=answer_choise,
                    widget=forms.CheckboxSelectMultiple,
                    required=False
                )

            else:
                self.fields[f'question_{question.id}_approve'] = forms.MultipleChoiceField(
                    label=f"{question.text}: Правильна відповідь {question_correct}",
                    choices=user_answers,
                    widget=forms.CheckboxSelectMultiple,
                    required=False,
                )
            
           

                