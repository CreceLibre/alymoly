#-*- encoding: UTF-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from AlyMoly.inventario.forms import StockCriticoForm, ReiniciarInventarioForm, \
        InventarioActualForm, BuscarExistenciaForm, ActualizarExistenciaForm
from AlyMoly.movimiento.models import ProductoBodega
from AlyMoly.mantenedor.models import Producto
from AlyMoly.utils.decorators import remote_method_only
import json
from django.db.models import F, Q

@staff_member_required
@remote_method_only("POST")
def actualizar_existencia(request):
    """Actualiza la existencia del producto de la bodega especificada"""
    form = ActualizarExistenciaForm(request.POST)
    if form.is_valid():
        existencia = form.cleaned_data['existencia']
        producto_bodega_id = form.cleaned_data['producto_bodega']
        producto_bodega = ProductoBodega.objects.get(pk=producto_bodega_id)
        producto_bodega.existencia = existencia
        producto_bodega.save()
        return HttpResponse()
    else:
        return HttpResponseBadRequest(json.dumps(form._errors),mimetype="application/json")

@staff_member_required
def criticos(request, bodega=None):
    """Muestra todos los productos en stock crítico
    (excluyendo productos compuestos)"""
    form = StockCriticoForm()
    if bodega:
        productos = ProductoBodega.objects.filter(
                             existencia__lte=F('producto__stock_critico'),
                             bodega=bodega).order_by('producto__nombre').select_related()
        return render_to_response('inventario/parcial/critico.html', {
            'productos' : productos.select_related(),
        })
    return render_to_response('inventario/critico.html', {
        'form': form,
    },context_instance=RequestContext(request))

@staff_member_required
def buscar(request, bodega):
    """Retorna el listado de productos resultantes basado
    en el siguiente criterio:
    EXACTO: codigo de barra
    PARCIAL: nombre, marca"""
    form = BuscarExistenciaForm(request.POST)
    if request.method == 'POST' and form.is_valid():
        search = form.cleaned_data['texto']
        inner_query = Producto.objects.exclude(
                                               compone__exact=None
                                               ).values_list('compone_id',flat=True)
        existencias = ProductoBodega.objects.filter(
                                                    bodega=bodega
                                                    ).exclude(
                                                              producto__in=inner_query
                                                              ).order_by('producto__nombre')
        existencias = existencias.filter(
                                         Q(producto__codigo_barra__exact=search) |
                                          Q(producto__nombre__icontains=search) |
                                          Q(producto__marca__icontains=search)
                                        )
        return render_to_response('inventario/parcial/actual.html', {
            'existencias' : existencias.select_related(),
        })


@staff_member_required
def actual(request, bodega=None):
    """ Se lista todo el inventario de la bodega seleccionada.
    Los productos compuestos son excluidos del listado."""
    form = InventarioActualForm()
    buscar_form = BuscarExistenciaForm()
    if bodega:
        id_compuestos = Producto.objects.exclude(compone=None).values_list('compone_id',flat=True)
        existencias = ProductoBodega.objects.filter(bodega=bodega).exclude(producto__in=id_compuestos).order_by('producto__nombre')
        return render_to_response('inventario/parcial/actual.html', {
            'existencias' : existencias.select_related(),
        })
    return render_to_response('inventario/actual.html', {
        'form': form, 'buscar_form': buscar_form,
    },context_instance=RequestContext(request))


@staff_member_required
def reiniciar(request):
    """ Se reinicia el inventario dado un valor. Para los
    productos compuestos, se establecen existencia 0 independiente
    del valor dado."""
    if request.method == 'POST':
        form = ReiniciarInventarioForm(request.POST)
        if form.is_valid():
            bodega = form.cleaned_data['bodega']
            valor = form.cleaned_data['valor_reinicio']
            ProductoBodega.objects.filter(bodega=bodega).update(existencia=0)
            id_compuestos = Producto.objects.exclude(compone=None).values_list('compone_id',flat=True)
            productos = ProductoBodega.objects.filter(bodega=bodega).exclude(producto__pk__in=id_compuestos)
            productos.update(existencia=valor)
            request.user.message_set.create(message="El inventario ha sido reiniciado satisfactoriamente.")

    else:
        form = ReiniciarInventarioForm()
    return render_to_response('inventario/reiniciar.html', {
        'form': form,
    },context_instance=RequestContext(request))
