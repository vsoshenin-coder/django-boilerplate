from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_TEACHER = 'TEACHER'
    ROLE_STUDENT = 'STUDENT'
    
    ROLE_CHOICES = [
        (ROLE_TEACHER, 'Педагог'),
        (ROLE_STUDENT, 'Студент'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT,
        verbose_name="Роль"
    )

    # Новые поля для учебного процесса
    department = models.CharField(
        max_length=150, 
        blank=True, 
        null=True, 
        verbose_name="Кафедра"
    )
    major = models.CharField(
        max_length=150, 
        blank=True, 
        null=True, 
        verbose_name="Направление обучения"
    )
    academic_group = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="Учебная группа"
    )

    def is_teacher(self):
        return self.role == self.ROLE_TEACHER

    def is_student(self):
        return self.role == self.ROLE_STUDENT
