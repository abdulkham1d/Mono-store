from django.contrib import admin

from apps.common.models import *
from apps.store.models import *


@admin.register(User_tg)
class UserTgAdmin(admin.ModelAdmin):
    list_display = ("username",)


