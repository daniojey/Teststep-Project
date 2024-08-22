from django.contrib import admin

from users.models import User, UsersGroup, UsersGroupMembership

admin.site.register(User)
admin.site.register(UsersGroup)
admin.site.register(UsersGroupMembership)