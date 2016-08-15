from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^producto/nombre/$',
        views.descripcion_producto,
        name='nombre_producto'),
    url(r'^producto/detalle/(?P<id>\d*)/$',
        views.detalle_producto,
        name='detalle_producto'),
    url(r'^sucursal/$',
        views.sucursal)
]
