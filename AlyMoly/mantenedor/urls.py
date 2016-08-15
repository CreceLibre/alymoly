from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^subcategorias/(?P<supercategoria_id>\d*)/$',
            views.subcategorias,
            name='subcategorias'),
    url(r'^subcategoria_de_producto/(?P<producto_id>\d*)/$',
        views.subcategoria_de_producto,
        name='subcategoria_de_producto'),
    url(r'^info_producto/(?P<producto_id>\d*)/$',
        views.info_producto,
        name='info_producto')
]
