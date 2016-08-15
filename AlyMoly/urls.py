#-*- encoding: UTF-8 -*-
from django.conf.urls import url, include
from settings import MEDIA_ROOT, DEBUG
from django.views.generic import RedirectView
from django.contrib import admin
from django.views.static import serve
admin.autodiscover()

handler500 = 'django.views.defaults.server_error'
handler404 = 'django.views.defaults.page_not_found'

urlpatterns = [
    url(r'^admin_tools/', include('admin_tools.urls')),
    url('^$', RedirectView.as_view(url='/venta/')),
    url(r'^admin/', include('AlyMoly.mantenedor.urls')),
    url(r'^admin/', include('AlyMoly.movimiento.urls')),
    url(r'^admin/reporte/', include('AlyMoly.reporte.urls', namespace='reporte')),
    url(r'^admin/inventario/', include('AlyMoly.inventario.urls', namespace='inventario')),
    url(r'^admin/utils/', include('AlyMoly.utils.urls', namespace='utils')),
    url(r'^venta/', include('AlyMoly.venta.urls')),
    url(r'^devolucion/', include('AlyMoly.devolucion.urls')),
    url(r'^admin/', include(admin.site.urls)),
]

if DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': MEDIA_ROOT,
        }),
    ]
