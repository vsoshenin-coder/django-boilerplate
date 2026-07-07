from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentProject(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название проекта")
    description = models.TextField(blank=True, verbose_name="Описание проекта")
    
    # Поле для загрузки 3D-модели. Файлы будут сохраняться в media/models/
    model_file = models.FileField(upload_to='models/', verbose_name="Файл 3D-модели (.gltf/.glb)")
    
    # Связываем проект со студентом, который его выложил
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_projects', verbose_name="Студент")
    
    # Оценка от преподавателя (может быть пустой при загрузке)
    grade = models.IntegerField(blank=True, null=True, verbose_name="Оценка")
    teacher_comment = models.TextField(blank=True, verbose_name="Комментарий преподавателя")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    def __str__(self):
        return f"{self.title} — {self.student.username}"

    class Meta:
        verbose_name = "Студенческий проект"
        verbose_name_plural = "Студенческие проекты"
