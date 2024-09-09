from django.contrib import admin
from tests.models import Categories, Tests, Question, Answer, TestResult, TestsReviews, QuestionGroup

admin.site.register(Tests)
admin.site.register(Question)
admin.site.register(QuestionGroup)
admin.site.register(Answer)
admin.site.register(TestResult)
admin.site.register(TestsReviews)

@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}




# @admin.register(Test

# @admin.register(Question)
# @admin.register(Answer)