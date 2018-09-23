from django.conf.urls import url

from support import views as support_views

app_name = 'support'

urlpatterns = [
    # Contacto para restablecer password en caso de que
    # haya un problema
    url(r'^accounts/contact/$', support_views.support_view,
        name='support-password'),
]
