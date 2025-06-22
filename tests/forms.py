from datetime import timedelta
from queue import PriorityQueue
import random
import re
from django import forms
from django.utils import timezone

from common.mixins import CacheMixin
from users.models import User, UsersGroupMembership
from .models import Categories, MatchingPair, QuestionGroup, Tests, Question, Answer, TestsReviews

class TestForm(CacheMixin,forms.ModelForm):
    raw_duration = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'placeholder': 'Введіть тривалість тесту в хвилинах'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        query = self.set_get_cache(Categories.objects.all(), "category_cache", 15)
        self.fields['category'].choices = [(item.id, item.name) for item in query]


    class Meta:
        model = Tests
        fields = ['name', 'description', 'image','category', 'check_type', 'date_in','date_out']
        widgets = {
            'name':forms.TextInput(attrs={'placeholder': 'Назва тесту'}),
            'image': forms.ClearableFileInput(attrs={
                'class': 'custom-file-input hidden',
                'id': 'uploadImage',
                # 'style': 'display: none;'  # Скрываем стандартный input
            }),
            # 'duration': forms.TextInput(attrs={
            #     'placeholder': 'Введіть тривалісь тесту гг:хх:сс)',
            # }),
            'category': forms.Select(attrs={'class': 'custom-select'}),
            'check_type': forms.Select(attrs={'class': 'custom-select'}),
            'date_in': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',  # опционально (для стилизации)
                    'min': f"{timezone.localtime().now().date()}T{timezone.localtime().now().time().strftime("%H:%M")}"
                    # 'min': f"{timezone.now().time().strftime("%H:%M")}"
                },
                format='%Y-%m-%dT%H:%M'     # обязательный формат
            ),
            'date_out': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',  # опционально (для стилизации)
                    'min': f"{timezone.localtime().now().date()}T{timezone.localtime().now().time().strftime("%H:%M")}"
                },
                format='%Y-%m-%dT%H:%M'     # обязательный формат
            )

        }

        name = forms.CharField(required=True)

        
    def clean_raw_duration(self):
        data = self.cleaned_data.get('raw_duration')

        if not data:
            raise forms.ValidationError("Поле тривалості тесту не може бути порожнім")
        
        if isinstance(data, timedelta):
            return data

        try:
            value = int(data)
        except ValueError:
            raise forms.ValidationError('Помилка, перевірте поле на правильність введеного часу')

        if value:
            result = timedelta(minutes=value)
        
            return result
        
        raise forms.ValidationError('Невідома помилка, перевірте поле')
        
        
        # pattern = r'(\d+)(г|хв|сек)'
        # match = re.match(pattern, data)
        # if not match:
        #     raise forms.ValidationError("Невірний формат часу, вкажіть вірний формат часу г|хв|сек")
        
        # value, unit = match.groups()
        # value = int(value)

        # if unit == 'г':
        #     result = timedelta(hours=value)
        # elif unit == 'хв':
        #     result = timedelta(minutes=value)
        # elif unit == 'сек':
        #     result = timedelta(seconds=value)
        # else:
        #     raise forms.ValidationError("Невідома одиниця виміру")
        
        # return result
    
    def clean_date_out(self):
        data = self.cleaned_data.get('date_out')
        return data
    

        
        # # Получаем группу, в которой состоит пользователь
        # user_group = UsersGroupMembership.objects.filter(user=self.user).first()
        # if user_group:
        #     # Получаем всех пользователей группы
        #     users_in_group = UsersGroupMembership.objects.filter(group=user_group.group)
        #     choices_user = [(user.user.id, user.user.username) for user in users_in_group]
            
        #     # Добавляем поле students с выбором
        #     self.fields['students'] = forms.MultipleChoiceField(
        #         choices=choices_user,
        #         widget=forms.CheckboxSelectMultiple,
        #         label="Оберіть студентів"
        #     )


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
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Назва групи'})
        }


class QuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        test = kwargs.pop('test', None)  # Забираем тест из kwargs
        super().__init__(*args, **kwargs)

         # Логика, скрывающая `answer_type` для вопросов, где оно не нужно
        # if self.instance.question_type in [Question.SINGLE_CHOICE, Question.MULTIPLE_CHOICE, Question.MATCHING]:
        #     self.fields.pop('answer_type', None)

        if test:
            question_groups = [('','Група питання')] + list(
                QuestionGroup.objects.filter(test=test).values_list('id', 'name')
            )

            self.fields['group'].choices = question_groups

            if question_groups:
                self.fields['group'].initial = question_groups[0]

            # Если тип проверки auto, убираем голосовую опцию для answer_type
            if test.check_type == 'auto':
                filtered_choices = [('', 'Тип відповіді')] + [
                    (choice, label) for choice, label in Question.ANSWER_TYPES if choice != Question.ANSWER_AUDIO
                ]
            else:
                filtered_choices = [('', 'Тип відповіді')] + [
                    (choice, label) for choice, label in Question.ANSWER_TYPES
                ]

            scores_types = [("", "Тип оцінювання")] + [
                (choice, label) for choice, label in Question.SCORE_FOR_TYPES
            ]

            self.fields['answer_type'].choices = filtered_choices
            self.fields['answer_type'].initial = filtered_choices[0]

            self.fields["scores_for"].choices = scores_types
            self.fields["scores_for"].initial = scores_types[0]
        else:
            self.fields['group'].queryset = QuestionGroup.objects.none()

        # Убираем пустой вариант и устанавливаем значение по умолчанию
        question_type = [('','Тип питання')] + [(choice, label) for choice, label in Question.QUESTION_TYPES]
        self.fields['question_type'].choices = question_type
        self.fields['question_type'].initial = question_type[0]

        self.fields['group'].required = False
        # self.fields['answer_type'].required = True

        


    class Meta:
        model = Question
        fields = ['text', 'question_type','image', 'audio', 'answer_type', 'group', 'scores_for' , 'scores']
        widgets = {
            'text': forms.TextInput(),
            'question_type': forms.Select(attrs={'class': 'custom-select', 'id': 'questionSelect'}),
            'image': forms.ClearableFileInput(attrs={
                'class': 'custom-file-input',
                'id': 'uploadImage',
                'style': 'display: none;'
                }

            ),
            'audio': forms.ClearableFileInput(attrs={
                'class': 'custom-file-input',
                'id': 'uploadAudio',
                'style': 'display: none;'
                }),
            'group': forms.Select(attrs={'class': 'custom-select'}),
            'answer_type': forms.Select(attrs={'class': 'custom-select', 'id': 'answerSelect', 'required': True}),
            'scores_for': forms.Select(attrs={"class": 'custom-select', 'id': 'scoresFor'}),
            'scores': forms.NumberInput(attrs={'class': 'number-input', 'required': False})
        }

    def clean_scores(self):
        score = self.cleaned_data.get('scores')
        scores_for = self.cleaned_data.get("scores_for")
        print(scores_for)
        print(score)

        if score < 0:
            raise forms.ValidationError('Поле балів повинно бути з позитивним значенням або 0')
        
        # if scores_for == "SA":
        #     score = 0
        #     print("Значение", score)
        # else:
        #     print("Без обновления")


        return score
    

class QuestionStudentsForm(CacheMixin ,forms.ModelForm):
    def __init__(self, *args, **kwargs):
        test = kwargs.pop('test', None)  # Текущий тест
        user = kwargs.pop('user', None)  # Текущий пользователь (учитель)
        super().__init__(*args, **kwargs)


        # Получаем группу, в которой состоит учитель
        user_group = UsersGroupMembership.objects.filter(user=user).select_related('group').first()
        
        if user_group:
            students_in_group = UsersGroupMembership.objects.filter(group=user_group.group).prefetch_related('user').values_list('user_id', 'user__username')

            # Список студентов для чекбоксов
            students = [(ids, username) for ids, username in students_in_group]

            
        else:
            students = [(user.id, user.username)]
        

        # Заполняем поле с чекбоксами
        self.fields['students'] = forms.MultipleChoiceField(
           choices=students,  # Список студентов в формате (id, имя)
           widget=forms.CheckboxSelectMultiple,
           label='Додати студентів до тесту',
           required=False
          )


        # Устанавливаем начальные значения для чекбоксов, если студенты уже выбраны
        if test and test.students:
            try:
                self.initial['students'] = [str(student_id) for student_id in test.students['students']]  # JSONField хранит список ID
            except Exception as e:
                print(f"У вашій группі на данний момент відсутні студенти {e}")


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
        fields = ['left_item', 'right_item', 'score']
        widgets = {
            'left_item': forms.TextInput(attrs={'placeholder': 'Ліва частина (Відповідність)'}),
            'right_item': forms.TextInput(attrs={'placeholder': 'Права частина (Відповідність)'}),
        }

    def clean_score(self):
        score = self.cleaned_data.get('score')

        if score < 0:
            raise forms.ValidationError('Поле балів повинно бути з позитивним значенням')
        
        return score

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text','score', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_score(self):
        score = self.cleaned_data.get('score')

        if score < 0:
            raise forms.ValidationError('Поле балів повинно бути з позитивним значенням')
        
        return score



class TestTakeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Теперь мы передаем только один вопрос
        question = kwargs.pop('question')  # Получаем текущий вопрос
        super().__init__(*args, **kwargs)

        choices = [(a.id, a.text) for a in question.answers.all()]
        random.shuffle(choices)  # Перемешиваем варианты ответа

        # Одиночный выбор (Single Choice)
        if question.question_type == 'TXT':
            if question.answer_type == 'SC':
                self.fields[f'answer'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=question.text
            )
                
            elif question.answer_type == 'MC':
                self.fields[f'answer'] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                label=question.text
            )
                
            elif question.answer_type == 'INP':
                self.fields[f'answer'] = forms.CharField(
                    label=f"{question.text}",
                    widget=forms.TextInput
                )

            elif question.answer_type == 'AUD':
                # Теперь ключ снова будет содержать ID вопроса
                self.fields[f'audio_answer_{question.id}'] = forms.CharField(
                    label=f"{question.text}",
                    widget=forms.HiddenInput(),  # Здесь будет сохраняться URL аудиофайла
                    required=False
                )

        
        # Выбор изображения (Image Choice)
        elif question.question_type == 'IMG':
            if question.answer_type == 'SC':
                self.fields[f'answer'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=question.text
            )
                
            elif question.answer_type == 'MC':
                self.fields[f'answer'] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                label=question.text
            )
                
            elif question.answer_type == 'INP':
                self.fields[f'answer'] = forms.CharField(
                    label=f"{question.text}",
                    widget=forms.TextInput
                )

            elif question.answer_type == 'AUD':
                # Теперь ключ снова будет содержать ID вопроса
                self.fields[f'audio_answer_{question.id}'] = forms.CharField(
                    label=f"{question.text} (Ваша відповідь в аудіо)",
                    widget=forms.HiddenInput(),  # Здесь будет сохраняться URL аудиофайла
                    required=False
                )
        
        # Аудио-вопросы (Audio Answer)
        elif question.question_type == 'AUD':
            if question.answer_type == 'SC':
                self.fields[f'answer'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=question.text
            )
                
            elif question.answer_type == 'MC':
                self.fields[f'answer'] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                label=question.text
            )
                
            elif question.answer_type == 'INP':
                self.fields[f'answer'] = forms.CharField(
                    label=f"{question.text}",
                    widget=forms.TextInput
                )

            elif question.answer_type == 'AUD':
                # Теперь ключ снова будет содержать ID вопроса
                self.fields[f'audio_answer_{question.id}'] = forms.CharField(
                    label=f"{question.text} (Ваша відповідь в аудіо)",
                    widget=forms.HiddenInput(),  # Здесь будет сохраняться URL аудиофайла
                    required=False
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
                
        # elif question.question_type == 'SC':
        #     self.fields[f'answer'] = forms.ChoiceField(
        #         choices=choices,
        #         widget=forms.RadioSelect,
        #         label=question.text
        #     )
        
        # Множественный выбор (Multiple Choice)
        # elif question.question_type == 'MC':
        #     self.fields[f'answer'] = forms.MultipleChoiceField(
        #         choices=choices,
        #         widget=forms.CheckboxSelectMultiple,
        #         label=question.text
        #     )


        # Текстовые ответы (Input Answer)
        # elif question.question_type == "INP":
        #     self.fields[f'answer'] = forms.CharField(
        #         label=f"{question.text}",
        #         widget=forms.TextInput
        #     )

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
        question = kwargs.pop('question', {})
        student_answer = kwargs.pop('student_question', None)
        print(question)
        print(student_answer)

        question_choises = [(a.id, a.text) for a in question.answers.all()]

        if question.answer_type == 'INP':
            answer = student_answer
        elif question.answer_type ==  Question.SINGLE_CHOICE:
            answer =  [Answer.objects.filter(id=int(student_answer)).first().id]
        elif question.question_type == "MTCH":
            answer = dict(student_answer)
        else:
            st_answers = Answer.objects.filter(id__in=student_answer)  # Получаем все ответы за один запрос
            answer= [a.id for a in st_answers]


        # test = kwargs.pop('test')
        # answers = kwargs.pop('answers')
        audio_answers = kwargs.pop('audio_answers', {})
        super().__init__(*args, **kwargs)

        # Проверяем, что вопрос существует
        if question is not None:
            # Текст вопроса (просто для отображения, не редактируемое поле)
            # self.fields['question_text'] = forms.CharField(
            #     label="Текст вопроса",
            #     initial=question.text,
            #     widget=forms.Textarea(attrs={'readonly': 'readonly'}),
            #     required=False,
            # )

            # Обработка различных типов ответов на основе типа ответа в вопросе
            if question.answer_type == Question.SINGLE_CHOICE:
                # Одиночный выбор (показ ответа студента)
                self.fields[f'answer'] = forms.ChoiceField(
                    choices=question_choises,
                    widget=forms.RadioSelect(),
                    initial=answer        

            )
            elif question.answer_type == Question.MULTIPLE_CHOICE:
                # Множественный выбор (выводим варианты через запятую)
                self.fields[f'answer'] = forms.MultipleChoiceField(
                choices=question_choises,
                widget=forms.CheckboxSelectMultiple(),
                label=question.text,
                initial=answer,
                )

            elif question.answer_type == Question.ANSWER_INPUT:
                # Текстовый ответ
                self.fields[f'answer'] = forms.CharField(
                    label=f"{question.text}",
                    widget=forms.TextInput(),
                    initial=answer
                )
            elif question.answer_type == Question.ANSWER_AUDIO:
                if question.text:
                    answer_text = question.text
                else:
                    answer_text = ''

                self.fields[f'audio_answer_{question.id}'] = forms.CharField(
                label=answer_text,
                widget=forms.HiddenInput(),
                required=False,
                initial=audio_answers.get(str(question.id))
            )
            elif question.question_type == Question.MATCHING:
                for i , (left_item, right_item) in enumerate(answer.items()):
                    # Левый элемент просто выводится как текст
                    self.fields[f'matching_left_{i}'] = forms.CharField(
                        label=left_item,
                        required=False,
                        widget=forms.HiddenInput()  # Прячем реальное поле, но текст останется как label
                    )

                    # Правый элемент также выводится как текст
                    self.fields[f'matching_right_{i}'] = forms.CharField(
                        label=right_item,
                        required=False,
                        widget=forms.HiddenInput()  # Прячем поле для выбора
                    )

            # # Если в вопросе есть изображение, добавляем его в форму для просмотра
            # if question.question_type == Question.IMAGE and question.image:
            #     self.fields['question_image'] = forms.CharField(
            #         label="Изображение вопроса",
            #         initial=question.image.url,
            #         widget=forms.TextInput(attrs={'readonly': 'readonly'}),
            #         required=False,
            #     )

            # Если в вопросе есть аудио, добавляем его в форму для просмотра
            # if question.question_type == Question.AUDIO:
            #     self.fields['question_audio'] = forms.CharField(
            #         label="Аудио вопроса",
            #         initial=question.audio.url,
            #         widget=forms.TextInput(attrs={'readonly': 'readonly'}),
            #         required=False,
            #     )

        # # Извлекаем ответы пользователя из JSON
        # user_answer_ids = answers.get(f'question_{question.id}', [])


        # # Получаем правильные ответы
        # item = question.answers.filter(is_correct=True)
        # ans = [i for i in item]
        # result = [i.text for i in ans]
        # question_correct = ', '.join(result)

        # # Получаем список  по ответам
        # try:
        #     user_answers =[
        #         (answer.id, answer.text) for answer in question.answers.filter(id__in=user_answer_ids)
        #     ]
        # except ValueError:
        #     ...

        # # Если одиночный ответ добавляем его вручную в список
        # if user_answers == [] and question.question_type == "SC":
        #     answer = question.answers.filter(id=user_answer_ids)[0]
        #     user_answers.append((answer.id, answer.text))


        # if question.question_type == 'MC':
        #     self.fields[f'question_{question.id}_approve'] = forms.MultipleChoiceField(
        #         label=f"{question.text}: Правильні відвопіді {question_correct}",
        #         choices=user_answers,
        #         widget=forms.CheckboxSelectMultiple,
        #         required=False,
                    
        #     )

        # elif question.question_type == 'AUD':  # Для вопросов с аудио
        #     self.fields[f'audio_answer_{question.id}'] = forms.CharField(
        #         label=f"Текст питання  {question.text}",
        #         widget=forms.HiddenInput(),
        #         required=False,
        #         initial=audio_answers.get(str(question.id))
        #     )

        #     self.fields[f"audio_answer_{question.id}_correct"] = forms.BooleanField(
        #         label=f"Відповідь вірна ?",
        #         required=False,
        #     )

        # elif question.question_type == 'INP':
        #     ans_resp = answers.get(f"question_{question.id}", None)
        #     item = item[0]
        #     self.fields[f'question_{question.id}_user_answer'] = forms.CharField(
        #         label=f"{question.text}:\nВірна відповідь ? - {item.text}",
        #         widget=forms.Textarea(attrs={'readonly': 'readonly'}),
        #         initial=f"Відповідь студента - {ans_resp}",
        #         required=False,
        #         )

        #     self.fields[f"question_{question.id}_correct"] = forms.BooleanField(
        #         label="Відповідь вірна ?",
        #         required=False,
        #         )
        # elif question.question_type == 'MTCH':
        #     answers_mtch = [f"{item.left_item}-{item.right_item}|" for item in MatchingPair.objects.filter(question=question)]
        #     user_answers = answers.get(f"question_{question.id}_type_matching", None)
        #     answer_choise = [(i, f"{key}-{value}") for i, (key, value) in enumerate(user_answers.items())]
        #     answers_mtch = " ".join(answers_mtch)

        #     self.fields[f'question_{question.id}_MT'] = forms.CharField(
        #         label=f"{question.text}:\nВірна відповідь ? ",
        #         widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        #         initial=answers_mtch,
        #         required=False,
        #     )

        #     self.fields[f"question_{question.id}_mtch"] = forms.MultipleChoiceField(
        #         label='Відповіді студента',
        #         choices=answer_choise,
        #         widget=forms.CheckboxSelectMultiple,
        #         required=False
        #     )

        # else:
        #     self.fields[f'question_{question.id}_approve'] = forms.MultipleChoiceField(
        #         label=f"{question.text}: Правильна відповідь {question_correct}",
        #         choices=user_answers,
        #         widget=forms.CheckboxSelectMultiple,
        #         required=False,
        #     )
            
           

                