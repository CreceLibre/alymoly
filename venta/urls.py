from django.conf.urls.defaults import url,patterns

urlpatterns = patterns('',
    (r'^venta/$','venta.views.venta'),
    (r'^cuerpo_venta/$','venta.views.cuerpo_venta'),
    ('^turno/abrir/$', 'venta.views.turno_abrir'),
    ('^turno/cerrar/$', 'venta.views.turno_cerrar'),
    (r'^$','venta.views.autentificacion'),
    (r'^elemento/add/(?P<cantidad_>\d+)/$','venta.views.agregar_elemento'),
    (r'^elemento/delete/(?P<codigo_barra_>\S+)/$','venta.views.eliminar'),
    (r'^elemento/aumentar/(?P<codigo_barra_>\S+)/$','venta.views.aumentar'),
    (r'^elemento/disminuir/(?P<codigo_barra_>\S+)/$','venta.views.disminuir'),    
    (r'^elemento/(?P<codigo_barra_>\S+)/$','venta.views.buscar_elemento'),
    (r'^medio_pago/(?P<medio_>\d+)/$','venta.views.medio_pago'),
    (r'^vuelto/(?P<cantidad_>\d+)/$','venta.views.calcular_vuelto'),
    (r'^registrar/$','venta.views.registrar_venta'),
    (r'^cabecera/$','venta.views.cabecera'),
    (r'^turno/cerrado/(?P<a_id>\d+)/$', 'venta.views.turno_cerrado'),
    url(r'^boleta/deposito/(?P<a_id>\d+)/$','venta.views.boleta_deposito', name="ver_boleta")   
)