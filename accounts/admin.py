from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    def get_fieldsets(self, request, obj=None):
        standard_fieldsets = super().get_fieldsets(request, obj)
        user_role = obj.role if obj else CustomUser.ROLE_STUDENT

        personal_fields = ['first_name', 'last_name', 'email']
        
        if user_role == CustomUser.ROLE_TEACHER:
            personal_fields.append('department')
        elif user_role == CustomUser.ROLE_STUDENT:
            personal_fields.extend(['major', 'academic_group'])

        custom_fieldsets = []
        for name, opts in standard_fieldsets:
            if not request.user.is_superuser and name in ['Permissions', 'Права доступа']:
                continue
            
            if name in ['Personal info', 'Персональная информация']:
                opts = opts.copy()
                opts['fields'] = tuple(personal_fields)
            
            custom_fieldsets.append((name, opts))

        has_role = any('role' in opts.get('fields', []) for name, opts in custom_fieldsets)
        if not has_role:
            custom_fieldsets.append(('Дополнительно', {'fields': ('role',)}))
        
        return tuple(custom_fieldsets)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        # Если зашел НЕ суперадмин — блокируем только критические системные поля
        if not request.user.is_superuser:
            extra_readonly = ['role', 'is_superuser', 'is_staff', 'groups', 'user_permissions']
            
            # Убираем поля из readonly, если стандартный UserAdmin их туда добавил
            # Это откроет Имя, Фамилию и Email для редактирования
            for field in ['first_name', 'last_name', 'email', 'username']:
                if field in readonly_fields:
                    readonly_fields.remove(field)

            for field in extra_readonly:
                if field not in readonly_fields:
                    readonly_fields.append(field)
                    
        return readonly_fields

    def has_change_permission(self, request, obj=None):
        """
        Разрешает пользователю редактировать профиль, 
        если он редактирует САМ СЕБЯ, либо если это суперадмин.
        """
        if request.user.is_superuser:
            return True
        if obj and obj.pk == request.user.pk:
            return True
        return super().has_change_permission(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        if not request.user.is_superuser and obj and 'password' in form.base_fields:
            change_password_url = f'../../{obj.pk}/password/'
            form.base_fields['password'].help_text = (
                f'<a href="{change_password_url}" class="btn btn-dark text-white">'
                f'Изменить пароль безопасности</a>'
            )
            form.base_fields['password'].widget = forms.HiddenInput()
            
        return form

admin.site.register(CustomUser, CustomUserAdmin)
