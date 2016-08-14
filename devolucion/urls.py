from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$','devolucion.views.devolucion'),
    (r'^cuerpo_devolucion/$','devolucion.views.cuerpo_devolucion'),
    #(r'^detalle_busqueda/$','devolucion.views.detalle_busqueda_devolucion'),
    #(r'^totales/(?P<a_cantidad>\d+)/$','devolucion.views.totales_devolucion'),
    (r'^elemento/add/(?P<cantidad_>\d+)/$','devolucion.views.agregar_elemento'),
    (r'^elemento/delete/(?P<codigo_barra_>\S+)/$','devolucion.views.eliminar'),
    (r'^elemento/aumentar/(?P<codigo_barra_>\S+)/$','devolucion.views.aumentar'),
    (r'^elemento/disminuir/(?P<codigo_barra_>\S+)/$','devolucion.views.disminuir'),    
    (r'^elemento/(?P<codigo_barra_>\S+)/$','devolucion.views.buscar_elemento'),    
    (r'^registrar/$','devolucion.views.registrar'),
    (r'^cabecera/$','devolucion.views.cabecera'),

#"""    
#    ('^turno/abrir/$', 'AlyMoly.venta.views.turno_abrir'),
#    ('^turno/cerrar/$', 'AlyMoly.venta.views.turno_cerrar'),
#    (r'^$','AlyMoly.venta.views.autentificacion'),
#    (r'^medio_pago/(?P<medio_>\d+)/$','AlyMoly.venta.views.medio_pago'),
#    (r'^vuelto/(?P<cantidad_>\d+)/$','AlyMoly.venta.views.calcular_vuelto'),
#    (r'^turno/cerrado/(?P<a_id>\d+)/$', 'AlyMoly.venta.views.turno_cerrado'),
#    (r'^boleta/deposito/(?P<a_id>\d+)/$','AlyMoly.venta.views.boleta_deposito')   
#"""
)