from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('',
    url(r'^bodega_sucursal/(?P<sucursal_id>\d*)/$', 
        'movimiento.views.bodega_sucursal', 
        name='bodega_sucursal'),

)