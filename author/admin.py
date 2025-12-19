from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from author.models import Author  # adjust import path if needed

class AuthorAdmin(UserAdmin):
    model = Author

    list_display = ('email_or_phone', 'username', 'email', 'phone', 'role', 'is_staff', 'is_active', 'is_verified')
    list_filter = ('role', 'is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('email_or_phone', 'password')}),
        ('Personal Info', {'fields': ('username', 'email', 'phone')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Role', {'fields': ('role',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email_or_phone', 'username', 'password1', 'password2', 'is_staff', 'is_active', 'role'),
        }),
    )

    search_fields = ('email_or_phone', 'username')
    ordering = ('email_or_phone',)

admin.site.register(Author, AuthorAdmin)
