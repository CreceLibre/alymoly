from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^productos/$',
        views.productos,
        name='productos'),
    url(r'^existencias/$',
        views.existencias,
        name='existencias'),
    url(r'^ventas/$',
        views.ventas,
        name='ventas'),
    url(r'^ventas/(?P<turno_id>\d*)/(?P<formato>pdf|html)/(?P<resumen>todos|afectos|exentos|promociones|devoluciones)/$',
        views.generar_ventas,
        name='generar_ventas'),
    url(r'^ventas/mes/$',
        views.ventas_mes,
        name='ventas_mes'),
    url(r'^ventas/grafico/categoria/$',
        views.ventas_graficos_periodo_categoria,
        name='ventas_graficos_periodo_categoria'),
    url('^$', TemplateView.as_view(template_name='reporte/index.html'), name="index"),
    url('^img/get', views.get_birt_img,
        name='get_birt_img'),
]
