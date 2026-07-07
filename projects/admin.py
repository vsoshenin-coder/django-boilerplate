from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import StudentProject

@admin.register(StudentProject)
class StudentProjectAdmin(admin.ModelAdmin):
    # ВАЖНО: 'model_preview' идет первой, чтобы встать наверх карточки-окошка в шаблоне
    list_display = ('model_preview', 'project_info')
    
    # Ссылкой для перехода внутрь карточки теперь будет весь текстовый блок информации
    list_display_links = ('project_info',)
    
    # Включает встроенную кнопку "Смотреть на сайте" внутри формы редактирования проекта
    view_on_site = True

    def model_preview(self, obj):
        if hasattr(obj, 'model_file') and obj.model_file:
            return format_html(
                '<div class="admin-3d-box js-3d-model-container" data-type="file" data-src="{}"></div>',
                obj.model_file.url
            )
        elif hasattr(obj, 'sketchfab_url') and obj.sketchfab_url and 'sketchfab.com' in obj.sketchfab_url:
            embed_url = obj.sketchfab_url.replace('/models/', '/models/').replace('sketchfab.com', '://sketchfab.com') + '/embed'
            return format_html(
                '<div class="admin-3d-box js-3d-model-container" data-type="iframe" data-src="{}"></div>',
                embed_url
            )
        return format_html('<div class="admin-3d-box" style="display:flex; align-items:center; justify-content:center; color:#999; font-size:12px; background:#f8fafc;">Нет 3D модели</div>')

    model_preview.short_description = "Превью модели"

        # 2. Генерируем структурированный текстовый блок информации под окошком
    def project_info(self, obj):
        student_name = obj.student.get_full_name() or obj.student.username
        
        # Передаем чистый текст и класс, а HTML соберем правильно внутри format_html
        if obj.grade:
            grade_text = f"Оценка: {obj.grade}"
            badge_class = "project-card-badge"
        else:
            grade_text = "Не проверено"
            badge_class = "project-card-badge empty"
            
        url = reverse('projects:project_detail', kwargs={'pk': obj.pk})
        
        # ИСПРАВЛЕНО: Безопасная подстановка всех переменных через {}
        return format_html(
            '<div class="project-card-title">{}</div>'
            '<div class="project-card-info" style="margin-top: 5px;">Автор: <strong>{}</strong></div>'
            '<div class="{}">{}</div>'
            '<div style="margin-top:12px;"><a href="{}" target="_blank" style="font-size:12px; text-decoration:underline; color:#79aec8; font-weight:bold;">Открыть сайт →</a></div>',
            obj.title, 
            student_name, 
            badge_class, 
            grade_text, 
            url
        )

        
    project_info.short_description = "Информация о проекте"

    # 3. Студент видит только свои работы, Педагог и Админ — абсолютно все
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        is_teacher = getattr(request.user, 'role', None) == 'TEACHER'
        if request.user.is_superuser or is_teacher:
            return qs
        return qs.filter(student=request.user)

    # 4. Ограничиваем редактирование полей оценки и автора для Студентов
    def get_readonly_fields(self, request, obj=None):
        if getattr(request.user, 'role', None) == 'STUDENT':
            return ('grade', 'teacher_comment', 'student')
        return super().get_readonly_fields(request, obj)

    # 5. Автоматически привязываем проект к текущему вошедшему студенту
    def save_model(self, request, obj, form, change):
        if getattr(request.user, 'role', None) == 'STUDENT' and not change:
            obj.student = request.user
        super().save_model(request, obj, form, change)

    # Разрешаем доступ к модулю админки абсолютно всем авторизованным пользователям
    def has_module_permission(self, request):
        return request.user.is_authenticated

    # Разрешаем просматривать страницу со списком проектов всем пользователям
    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

   # Измените этот метод в вашем файле admin.py:
    def has_add_permission(self, request):
        # Разрешаем добавлять проекты абсолютно всем авторизованным пользователям
        return request.user.is_authenticated