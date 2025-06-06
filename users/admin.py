from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.views import View
from django.views.generic import FormView, TemplateView, View

from users.models import EmailTestNotyficateUser, User, UsersGroup, UsersGroupMembership, LoginAttempt
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

@admin.register(UsersGroup)
class UserGroupAdmin(ModelAdmin):
    search_fields = ['name']

@admin.register(UsersGroupMembership)
class UserGroupMembershipAdmin(ModelAdmin):
    list_select_related = True
    list_display  = ["user", "group", "owner"]
    search_fields = ["user__first_name", "user__last_name", "user__username", "group__name", "owner"]

@admin.register(LoginAttempt)
class LoginAttemptAdmin(ModelAdmin):
    pass


class CreateUsersView(UnfoldModelAdminViewMixin, TemplateView):
    title="Додати студентів"
    template_name = "admin/add_users.html"
    permission_required = ()


@admin.register(EmailTestNotyficateUser)
class EmailTestNotifyAdmin(ModelAdmin):
    list_display = ['test', 'user']


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
    