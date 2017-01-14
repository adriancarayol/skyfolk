from django.conf.urls import url

urlpatterns = [
    # Contacto para restablecer password en caso de que
    # haya un problema
    url(r'^accounts/contact/$', 'support.views.support_view',
        name='support-password'),
]