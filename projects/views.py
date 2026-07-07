from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import StudentProject

# === ДОБАВЛЯЕМ: Представление для главной страницы с 3D-галереей ===
@login_required # Только для авторизованных пользователей
def home_view(request):
    # 1. Извлекаем проекты из БД, у которых загружен 3D-файл
    projects_queryset = StudentProject.objects.exclude(model_file="").select_related('student')
    
    # 2. Превращаем QuerySet в чистый Python-список из словарей, 
    # чтобы Django-фильтр json_script смог легко переварить его в JSON без ошибок
    projects_list = []
    for project in projects_queryset:
        projects_list.append({
            "id": project.pk,
            "title": project.title,
            "model_file": project.model_file.url if project.model_file else ""
        })
        
    # 3. Отправляем этот список в шаблон home.html
    return render(request, 'home.html', {'projects_data_json': projects_list})


# === ВАШ ТЕКУЩИЙ КОД (ОСТАЕТСЯ БЕЗ ИЗМЕНЕНИЙ) ===
@login_required 
def project_detail(request, pk):
    project_object = get_object_or_404(StudentProject, pk=pk)
    
    user = request.user
    is_teacher = getattr(user, 'role', None) == 'TEACHER'
    
    if not user.is_superuser and not is_teacher and project_object.student != user:
        raise PermissionDenied("У вас нет прав для просмотра этого проекта.")
    
    return render(request, 'projects/project_detail.html', {'project': project_object})
