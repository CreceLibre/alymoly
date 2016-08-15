from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^venta/$',views.venta),
    url(r'^cuerpo_venta/$',views.cuerpo_venta),
    url('^turno/abrir/$', views.turno_abrir),
    url('^turno/cerrar/$', views.turno_cerrar),
    url(r'^$',views.autentificacion),
    url(r'^elemento/add/(?P<cantidad_>\d+)/$',views.agregar_elemento),
    url(r'^elemento/delete/(?P<codigo_barra_>\S+)/$',views.eliminar),
    url(r'^elemento/aumentar/(?P<codigo_barra_>\S+)/$',views.aumentar),
    url(r'^elemento/disminuir/(?P<codigo_barra_>\S+)/$',views.disminuir),
    url(r'^elemento/(?P<codigo_barra_>\S+)/$',views.buscar_elemento),
    url(r'^medio_pago/(?P<medio_>\d+)/$',views.medio_pago),
    url(r'^vuelto/(?P<cantidad_>\d+)/$',views.calcular_vuelto),
    url(r'^registrar/$',views.registrar_venta),
    url(r'^cabecera/$',views.cabecera),
    url(r'^turno/cerrado/(?P<a_id>\d+)/$', views.turno_cerrado),
    url(r'^boleta/deposito/(?P<a_id>\d+)/$',views.boleta_deposito, name="ver_boleta")
]
