from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^critico/$', 
        'inventario.views.criticos',
        name='criticos'),
    url(r'^critico/(?P<bodega>\d*)/$', 
        'inventario.views.criticos'),
    url(r'^reiniciar/$', 
        'inventario.views.reiniciar',
        name='reiniciar'),
    url(r'^actual/$', 
        'inventario.views.actual',
        name='actual'),
    url(r'^actual/(?P<bodega>\d*)/$', 
        'inventario.views.actual'),
    url(r'^buscar/(?P<bodega>\d*)/$', 
        'inventario.views.buscar'),
    url(r'^existencia/actualizar/$', 
        'inventario.views.actualizar_existencia', 
        ),
    url('^$', direct_to_template, {
        'template': 'inventario/index.html'
    }, name="index")
)