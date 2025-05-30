from django.contrib import admin
from django.db.models import Q
from django.utils.timezone import localtime
from tests.forms import TestsAdminForm
from tests.models import Categories, MatchingPair, Tests, Question, Answer, TestResult, TestsReviews, QuestionGroup
from users.models import User
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import TextFilter, FieldTextFilter
from django.core.validators import EMPTY_VALUES
from django.utils.translation import gettext_lazy as _


# admin.site.register(Tests)
# admin.site.register(Question)
# admin.site.register(QuestionGroup)
# admin.site.register(Answer)
# admin.site.register(MatchingPair)
# admin.site.register(TestResult)
# admin.site.register(TestsReviews)

class CustomTestFilter(TextFilter):
    title = _("Фільтер по тестам")
    parameter_name = "tests"

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            # Here write custom query
            return queryset.filter(test__name__icontains=self.value())

        return queryset
    

class CustomQuestionFilter(TextFilter):
    title = _("Фільтр по питанням")
    parameter_name = "question"

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            return queryset.filter(question__text__icontains=self.value())

        return queryset


class CustomUserFilter(TextFilter):
    title = "Фільтр по студентам"
    parameter_name = "user"

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            return queryset.filter(Q(user__first_name__icontains=self.value()) | Q(user__last_name__icontains=self.value()) | Q(user__username__icontains=self.value()))

        return queryset
    

@admin.display(description="Назва тесту")
def test_name(obj):
    text = obj.test.name
    return text[:40]

@admin.display(description="Текст питання")
def question_text(obj):
    if obj.text:
        return str(obj.text)[:35]
    else:
        return f"{obj.question_type}"

@admin.display(description="Група питань")
def question_group_name(obj):
    if obj.group:
        return f"{obj.group.name}"
    else:
        return "Без группы"

@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_select_related = True
    list_display = [test_name,  question_text, question_group_name, "question_type", "answer_type", "scores"]
    search_fields = [
        "test__name",
        "group__name",
        "text",
        "question_type",
        "answer_type",
        "scores"
        ]
    
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        CustomTestFilter,
    ]

@admin.register(QuestionGroup)
class QuestionGroupAdmin(ModelAdmin):
    list_display = [test_name, "name"]
    search_fields = ["test__name", "name"]
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        CustomTestFilter,
    ]

@admin.display(description="Текст питання")
def question_text_answer(obj):
    if obj.question.text:
        return str(obj.question.text)[:35]
    else:
        return f"{obj.question.question_type}"
    

@admin.display(description="Текст відповіді")
def question_text(obj):
    if obj.text:
        return str(obj.text)[:35]
    else:
        return f"{obj.question_type}"

@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_select_related = True
    list_display = [question_text_answer, question_text, "is_correct", "score"]
    search_fields = ["question", "text", "is_correct"]
    list_filter_submit = True  # Submit button at the bottom of the filter
    search_fields = ["question__text", "text"]
    list_filter = [
        CustomQuestionFilter,

    ]

@admin.register(MatchingPair)
class MatchingPairAdmin(ModelAdmin):
    list_select_related = True
    list_display = ["question", "left_item", "right_item", "score"]
    search_fields = ["question__text", "left_item", "right_item"]
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        CustomQuestionFilter,

    ]

@admin.display(description="Бали")
def test_score(obj):
    return f"{int(obj.score)}%"

@admin.register(TestResult)
class TestResultAdmin(ModelAdmin):
    list_select_related = True
    list_display = [
        "user",
        test_name,
        test_score,
        "date_taken",
        "duration",
        ]
    list_display_links = [test_name]
    
    search_fields = ["user__username","user__first_name","user__last_name", 'test__name', 'score']
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        CustomTestFilter,
        CustomUserFilter,

    ]

@admin.register(TestsReviews)
class TestReviewsAdmin(ModelAdmin):
    list_select_related = True
    list_display = [test_name, "user", "date_taken", "duration"]
    search_fields = ["test__name", "user__username", "user__first_name", "user__last_name", "date_taken", "duration"]
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        CustomTestFilter,
        CustomUserFilter,

    ]


@admin.register(Categories)
class CategoriesAdmin(ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.display(description="Доступний до")
def date_in(obj):
    return f"{localtime(obj.date_in).date()}:{localtime(obj.date_in).time()}"

@admin.display(description="Доступний до")
def date_out(obj):
    return f"{localtime(obj.date_out).date()}:{localtime(obj.date_out).time()}"

class TestsAdmin(ModelAdmin):
    list_display = ["user","name","duration","date_taken",date_in,date_out, 'category', "check_type"]
    list_display_links = ('name',)
    form = TestsAdminForm  # Подключаем кастомную форму к админке
    search_fields = ['name']
    list_filter = [
        ("name", FieldTextFilter),
    ]
    list_filter_submit = True 

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # Если тест уже создан, показываем пользователей
            form.base_fields['students'].queryset = User.objects.all()
        else:  # Если тест создается, то поле пустое
            form.base_fields['students'].queryset = User.objects.none()
        return form


admin.site.register(Tests, TestsAdmin)

# @admin.register(Tests, TestsAdmin)
# class TestsAdmin(ModelAdmin):
#     pass


# @admin.register(Test

# @admin.register(Question)
# @admin.register(Answer)