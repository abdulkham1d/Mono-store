from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.users.models import User, Token


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),

        (_("Personal info"), {"fields": ("first_name",)}),

        (_("Permissions"),
         {
             "fields": ("is_active",
                        "is_staff",
                        "is_superuser",
                        "groups",
                        "user_permissions"),
         }),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "usable_password", "password1", "password2"),
        }),
    )
    list_display = ('first_name', 'username', 'is_staff')
    search_fields = ("username", "first_name")
    ordering = ("username",)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    ...
