from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from django.urls import reverse

class UserDashboardRedirectView(LoginRequiredMixin, RedirectView):
    """
    Представление для перенаправления всех авторизованных пользователей
    (и педагогов, и студентов) напрямую в панель управления Django.
    """
    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        # Перенаправляем любого вошедшего пользователя в корень админки.
        # reverse('admin:index') безопасно генерирует путь '/admin/'
        return reverse('admin:index')
