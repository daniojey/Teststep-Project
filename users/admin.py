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
    pass

@admin.register(UsersGroup)
class UserGroupAdmin(ModelAdmin):
    pass

@admin.register(UsersGroupMembership)
class UserGroupMembershipAdmin(ModelAdmin):
    pass

@admin.register(LoginAttempt)
class LoginAttemptAdmin(ModelAdmin):
    pass