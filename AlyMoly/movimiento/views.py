#-*- encoding: UTF-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from AlyMoly.mantenedor.models import Bodega, Producto
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def bodega_sucursal(request, sucursal_id):
    """Retorna todas las bodegas de una sucursal"""
    return HttpResponse(serializers.serialize('json',
                                              Bodega.objects.filter(sucursal=sucursal_id),
                                                                        fields=('pk','ubicacion')
                                                                    )
                                            )
