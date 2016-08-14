#-*- encoding: UTF-8 -*-
from mantenedor.models import Producto
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseBadRequest
from utils.forms import NombreProductoForm
from utils.decorators import remote_method_only
import json
from settings import SUCURSAL_NOMBRE
from django.forms.models import model_to_dict


@staff_member_required
@remote_method_only('GET')
def descripcion_producto(request):
    """Retorna la información de un producto, dado su código de barra."""
    form = NombreProductoForm(request.GET)
    if form.is_valid():
        parent=Producto.objects.get(codigo_barra=form.cleaned_data['codigo_barra'])
        parent_desc = parent.__unicode__()
        child_desc = None
        try:
            child = Producto.objects.get(compone=parent)
            child_desc = "%s, %s unidad(es)." % (child.__unicode__() , child.cantidad_compone)
        except Producto.DoesNotExist:
            pass
        return HttpResponse(json.dumps((parent_desc, child_desc)), mimetype="application/json")
    else:
        return HttpResponseBadRequest(json.dumps(form._errors),mimetype="application/json")

@staff_member_required
def detalle_producto(request,id):
    """Retorna el código de barra de un producto, dado su código de barra."""
    producto=None
    try:
        producto = Producto.objects.get(id=id)
    except Producto.DoesNotExist:
        return HttpResponseBadRequest()
    data = model_to_dict(producto)
    return HttpResponse(json.dumps(data),mimetype="application/json")

def sucursal(request):
    return HttpResponse(json.dumps({'nombre_sucursal':SUCURSAL_NOMBRE}),content_type="text/plain")
        
