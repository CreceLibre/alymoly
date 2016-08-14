from django.conf.urls.defaults import url, patterns
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^productos/$', 
        'reporte.views.productos', 
        name='productos'),              
    url(r'^existencias/$', 
        'reporte.views.existencias', 
        name='existencias'),
    url(r'^ventas/$', 
        'reporte.views.ventas', 
        name='ventas'),
    url(r'^ventas/(?P<turno_id>\d*)/(?P<formato>pdf|html)/(?P<resumen>todos|todos_detalle|afectos|exentos|promociones|devoluciones|stock_critico)/$', 
    'reporte.views.generar_ventas', 
    name='generar_ventas'),
    url(r'^ventas/mes/$', 
        'reporte.views.ventas_mes', 
        name='ventas_mes'),
    url(r'^ventas/grafico/categoria/$', 
        'reporte.views.ventas_graficos_periodo_categoria', 
        name='ventas_graficos_periodo_categoria'),    
    url('^$', direct_to_template, {
        'template': 'reporte/index.html'
    }, name="index"), 
    url('^img/get','reporte.views.get_birt_img',
        name='get_birt_img'),
)