from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings  # Добавили импорт настроек
from django.conf.urls.static import static  # Добавили импорт для статики
from accounts.views import UserDashboardRedirectView
from projects.views import home_view 

def home(request):
    return HttpResponse("Hello, world. This is a django boilerplate!")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path('', home_view, name='home'),
    # 1. Подключаем маршруты для отображения 3D-проектов
    path("projects/", include("projects.urls")),
    
    path("", home, name="home"),
    path("dashboard/redirect/", UserDashboardRedirectView.as_view(), name="dashboard_redirect"),
]

# 2. Разрешаем Django открывать загруженные 3D-модели в браузере (только для режима разработки)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
