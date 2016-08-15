from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^critico/$',
        views.criticos,
        name='criticos'),
    url(r'^critico/(?P<bodega>\d*)/$',
        views.criticos),
    url(r'^reiniciar/$',
        views.reiniciar,
        name='reiniciar'),
    url(r'^actual/$',
        views.actual,
        name='actual'),
    url(r'^actual/(?P<bodega>\d*)/$',
        views.actual),
    url(r'^buscar/(?P<bodega>\d*)/$',
        views.buscar),
    url(r'^existencia/actualizar/$',
        views.actualizar_existencia
        ),
    url('^$', TemplateView.as_view(
        template_name='inventario/index.html'), name="index")
]
