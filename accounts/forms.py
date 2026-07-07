from django import forms
from allauth.account.forms import SignupForm, LoginForm
from django.contrib.auth.models import Group
from .models import CustomUser

class CustomSignupForm(SignupForm):
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Кто вы?"
    )

    def save(self, request):
        # Сохраняем базового пользователя через allauth
        user = super().save(request)
        user.role = self.cleaned_data['role']
        
        # Обязательно даем статус персонала ВСЕМ, чтобы пускало в консоль админки
        user.is_staff = True
        user.save() # Сохраняем для генерации ID в базе данных
        
        # Распределяем роли по группам прав
        if user.role == 'TEACHER':
            teacher_group, created = Group.objects.get_or_create(name='Педагоги')
            user.groups.add(teacher_group)
        else:
            student_group, created = Group.objects.get_or_create(name='Студенты')
            user.groups.add(student_group)
            
        return user

class CustomLoginForm(LoginForm):
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Войти как",
        required=False
    )
