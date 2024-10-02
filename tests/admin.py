from django.contrib import admin
from tests.forms import TestsAdminForm
from tests.models import Categories, MatchingPair, Tests, Question, Answer, TestResult, TestsReviews, QuestionGroup
from users.models import User

# admin.site.register(Tests)
admin.site.register(Question)
admin.site.register(QuestionGroup)
admin.site.register(Answer)
admin.site.register(MatchingPair)
admin.site.register(TestResult)
admin.site.register(TestsReviews)


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}



class TestsAdmin(admin.ModelAdmin):
    form = TestsAdminForm  # Подключаем кастомную форму к админке

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # Если тест уже создан, показываем пользователей
            form.base_fields['students'].queryset = User.objects.all()
        else:  # Если тест создается, то поле пустое
            form.base_fields['students'].queryset = User.objects.none()
        return form

admin.site.register(Tests, TestsAdmin)


# @admin.register(Test

# @admin.register(Question)
# @admin.register(Answer)