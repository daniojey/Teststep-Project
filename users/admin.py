from django.contrib import admin

from users.models import User, UsersGroup, UsersGroupMembership, LoginAttempt
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from unfold.admin import ModelAdmin

# admin.site.register(User)
# admin.site.register(UsersGroup)
# admin.site.register(UsersGroupMembership)
# admin.site.register(LoginAttempt)

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ["first_name","last_name", "username", "email"]
    search_fields = ["first_name","last_name", "username", "email"]

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