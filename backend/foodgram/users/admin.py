from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ApiUser


@admin.register(ApiUser)
class ApiUserAdmin(UserAdmin):
    pass
