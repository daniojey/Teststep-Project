from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.views import View
from django.views.generic import FormView, TemplateView, View

from users.models import EmailTestNotyficateUser, User, LoginAttempt, Group
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from unfold.admin import ModelAdmin
from unfold.views import UnfoldModelAdminViewMixin

# admin.site.register(User)
# admin.site.register(UsersGroup)
# admin.site.register(UsersGroupMembership)
# admin.site.register(LoginAttempt)

# @admin.register(User)
# class UserAdmin(ModelAdmin):
#     list_display = ["first_name","last_name", "username", "email"]
#     search_fields = ["first_name","last_name", "username", "email"]



class CreateUsersView(UnfoldModelAdminViewMixin, TemplateView):
    title="Додати студентів"
    template_name = "admin/add_users.html"
    permission_required = ()


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    filter_horizontal = ('members',)
    list_display= ['name']
    search_fields = ['name']


@admin.register(EmailTestNotyficateUser)
class EmailTestNotifyAdmin(ModelAdmin):
    list_display = ['test', 'user']

@admin.register(LoginAttempt)
class LoginAttempt(ModelAdmin):
    search_fields = ['email', 'ip_address']
    list_display = ['email', 'timestamp', 'success']


@admin.register(User)
class UserModelAdmin(ModelAdmin):
    list_display = ["first_name","last_name", "username", "email"]
    search_fields = ["first_name","last_name", "username", "email"]

    def get_urls(self):
        urls = super().get_urls()
        custom_view = self.admin_site.admin_view(CreateUsersView.as_view(model_admin=self))

        my_urls = [
            path(
                'adding_students',
                custom_view,
                name="adding_students",
            )
        ]

        return my_urls + urls
    