from django.contrib import admin
from django.db.models import Q
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


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        CustomTestFilter,
    ]

@admin.register(QuestionGroup)
class QuestionGroupAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        CustomTestFilter,
    ]

@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        CustomQuestionFilter,

    ]

@admin.register(MatchingPair)
class MatchingPairAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        CustomQuestionFilter,

    ]

@admin.register(TestResult)
class TestResultAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        CustomTestFilter,
        CustomUserFilter,

    ]

@admin.register(TestsReviews)
class TestReviewsAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = [
        CustomTestFilter,
        CustomUserFilter,

    ]


@admin.register(Categories)
class CategoriesAdmin(ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}



class TestsAdmin(ModelAdmin):
    form = TestsAdminForm  # Подключаем кастомную форму к админке
    list_filter = [
        ("name", FieldTextFilter),
    ]

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