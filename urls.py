#-*- encoding: UTF-8 -*-
from django.conf.urls.defaults import include, patterns, url
from settings import MEDIA_ROOT, DEBUG
from django.contrib import admin
admin.autodiscover()

handler500 = 'django.views.defaults.server_error'
handler404 = 'django.views.defaults.page_not_found'

urlpatterns = patterns('',
    url(r'^admin_tools/', include('admin_tools.urls')),
    ('^$', 'django.views.generic.simple.redirect_to', {'url': '/venta/'}),
    (r'^admin/', include('mantenedor.urls')),
    (r'^admin/', include('movimiento.urls')),
    (r'^admin/reporte/', include('reporte.urls', namespace='reporte')),
    (r'^admin/inventario/', include('inventario.urls', namespace='inventario')),
    (r'^admin/utils/', include('utils.urls', namespace='utils')),
    (r'^venta/',include('venta.urls')),
    (r'^devolucion/',include('devolucion.urls')),    
    (r'^admin/', include(admin.site.urls)),

)

if DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': MEDIA_ROOT, 'show_indexes': True}),

    )

