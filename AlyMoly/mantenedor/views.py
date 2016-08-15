#-*- encoding: UTF-8 -*-
from django.http import HttpResponse
from django.core import serializers
from django.contrib.admin.views.decorators import staff_member_required
from AlyMoly.mantenedor.models import Categoria, Producto
import json

@staff_member_required
def info_producto(request,producto_id):
    """Retorna la información de un producto, dado su id."""
    return HttpResponse(Producto.objects.get(pk=producto_id))

@staff_member_required
def subcategorias(request, supercategoria_id):
    """Retorna todas las subcategorías de una categoría superior."""
    return HttpResponse(serializers.serialize('json',
                                              Categoria.objects.filter(supercategoria=supercategoria_id),
                                                                        fields=('pk','nombre')
                                                                        )
                                            )
@staff_member_required
def subcategoria_de_producto(request, producto_id):
    """Retorna el codigo de categoría y de subcategoría de un producto dado."""
    producto = Producto.objects.get(pk=producto_id)
    categoria = Categoria.objects.get(pk=producto.subcategoria_id)
    supercategoria = ''
    try:
        supercategoria = categoria.supercategoria.id
        subcategoria = categoria.id
    except AttributeError:
        supercategoria = categoria.id
        subcategoria = None
    return HttpResponse(json.dumps({'supercategoria':supercategoria,'subcategoria':subcategoria}))
