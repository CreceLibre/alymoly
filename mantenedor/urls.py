from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('',
    url(r'^subcategorias/(?P<supercategoria_id>\d*)/$', 
            'mantenedor.views.subcategorias', 
            name='subcategorias'),
    url(r'^subcategoria_de_producto/(?P<producto_id>\d*)/$', 
        'mantenedor.views.subcategoria_de_producto', 
        name='subcategoria_de_producto'),
    url(r'^info_producto/(?P<producto_id>\d*)/$', 
        'mantenedor.views.info_producto', 
        name='info_producto'),
)