from django.urls import path
# ИСПРАВЛЕНО: Добавили home_view в импорт через запятую
from .views import project_detail, home_view 

app_name = 'projects'

urlpatterns = [
    # Страница детального просмотра (например: /projects/5/)
    path('<int:pk>/', project_detail, name='project_detail'), 
    
    # Главная страница галереи внутри приложения (адрес: /projects/)
    path('', home_view, name='home'),
]
