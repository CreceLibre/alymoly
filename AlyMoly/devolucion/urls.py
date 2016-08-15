from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.devolucion),
    url(r'^cuerpo_devolucion/$',views.cuerpo_devolucion),
    #(r'^detalle_busqueda/$',views.detalle_busqueda_devolucion),
    #(r'^totales/(?P<a_cantidad>\d+)/$',views.totales_devolucion),
    url(r'^elemento/add/(?P<cantidad_>\d+)/$',views.agregar_elemento),
    url(r'^elemento/delete/(?P<codigo_barra_>\S+)/$',views.eliminar),
    url(r'^elemento/aumentar/(?P<codigo_barra_>\S+)/$',views.aumentar),
    url(r'^elemento/disminuir/(?P<codigo_barra_>\S+)/$',views.disminuir),
    url(r'^elemento/(?P<codigo_barra_>\S+)/$',views.buscar_elemento),
    url(r'^registrar/$',views.registrar),
    url(r'^cabecera/$',views.cabecera)
]
