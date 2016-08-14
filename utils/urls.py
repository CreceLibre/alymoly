from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^producto/nombre/$', 
        'utils.views.descripcion_producto', 
        name='nombre_producto'),
    url(r'^producto/detalle/(?P<id>\d*)/$', 
        'utils.views.detalle_producto', 
        name='detalle_producto'),
    url(r'^sucursal/$', 
        'utils.views.sucursal'),
)