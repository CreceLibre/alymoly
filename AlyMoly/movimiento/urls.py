from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^bodega_sucursal/(?P<sucursal_id>\d*)/$',
        views.bodega_sucursal,
        name='bodega_sucursal'),
]
