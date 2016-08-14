#-*- encoding: UTF-8 -*-
from django.shortcuts import render_to_response
from reporte.forms import ExistenciaPorCategoriaForm, \
                         VentasPorTurnoForm, BuscarTurnoForm, \
                         ProductoForm, VentaMesForm, VentasGraficosForm, \
                         VentasGraficosPorCategoriaForm
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from reporte.clases import ExistenciaPorCategoria, VentasPorTurno, Existencias, \
                        Productos, Promociones, ProductosAfectos, ProductosExentos, \
                        ProductosCodigoBarra, ProductosCodigoManual, VentasPorTurnoResumenAfectos, \
                        VentasPorTurnoResumenDevoluciones, VentasPorTurnoResumenExentos, \
                        VentasPorTurnoResumenPromociones, VentasPorTurnoResumenStockCritico, \
                        VentasPorTurnoDetalle, VentasPorMes, VentasGraficoProducto, VentasGraficoPromocion, \
                        VentasGraficoProductoPorCategoria, VentasGraficoPromocionPorCategoria, \
                        VentasPorMesResumido
from venta.models import Turno
from django.template import RequestContext
from datetime import datetime
from django.db.models import Max, Min
from settings import REPORT_IMAGE_DIR

import fnmatch
import os

@staff_member_required
def productos(request):
    """Vista que genera un reporte de producto"""
    if request.method == 'POST': 
        form = ProductoForm(request.POST)
        if form.is_valid():
            tipo = int(form.cleaned_data['tipo_producto'])
            reporte = {
                ProductoForm.TODOS : Productos(form.cleaned_data),
                ProductoForm.CODIGO_BARRA : ProductosCodigoBarra(form.cleaned_data),
                ProductoForm.CODIGO_MANUAL: ProductosCodigoManual(form.cleaned_data),
                ProductoForm.EXENTOS : ProductosExentos(form.cleaned_data),
                ProductoForm.AFECTOS : ProductosAfectos(form.cleaned_data),
                ProductoForm.PROMOCIONES : Promociones(form.cleaned_data)
            }[tipo]
            return reporte.get_response()
    else:
        form = ProductoForm() 

    return render_to_response('reporte/productos.html', {
        'form': form,
    },context_instance=RequestContext(request))

@staff_member_required
def existencias(request):
    """Vista que genera un reporte de existencias por categoria"""
    if request.method == 'POST': 
        form = ExistenciaPorCategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.cleaned_data['categoria']
            if categoria == u'-1':
                reporte = Existencias(form.cleaned_data)
            else:
                reporte = ExistenciaPorCategoria(form.cleaned_data)
            return reporte.get_response()
    else:
        form = ExistenciaPorCategoriaForm() 

    return render_to_response('reporte/existencias.html', {
        'form': form,
    },context_instance=RequestContext(request))
    
@staff_member_required
def ventas(request):
    """Vista que genera un reporte de ventas por 
    turno"""
    response = {}
    if request.method == 'POST': 
        form = VentasPorTurnoForm(request.POST)
        if form.is_valid():
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_inicio = datetime(fecha_inicio.year,fecha_inicio.month, fecha_inicio.day,0,0,0,0)
            fecha_fin = form.cleaned_data['fecha_fin']
            fecha_fin = datetime(fecha_fin.year,fecha_fin.month, fecha_fin.day,23,59,59,999999)
            turnos = None
            turnos = Turno.objects.filter(
                                       fecha_apertura_sistema__range=(fecha_inicio, fecha_fin)
                                        ).order_by('fecha_apertura_sistema')
            search_form = BuscarTurnoForm()
            response.update({'search_form':search_form,'turnos':turnos})

    else:
        form = VentasPorTurnoForm() 
        
    response.update({'form':form})
    return render_to_response('reporte/ventas.html', response,
                              context_instance=RequestContext(request))

@staff_member_required
def generar_ventas(request,turno_id,formato,resumen):
    """Vista que genera un reporte de ventas por 
    turno"""
    reporte = {
        'todos' : VentasPorTurno({'turno':turno_id,'formato':formato}),
        'todos_detalle': VentasPorTurnoDetalle({'turno':turno_id,'formato':formato}),
        'exentos' : VentasPorTurnoResumenExentos({'turno':turno_id,'formato':formato}),
        'afectos': VentasPorTurnoResumenAfectos({'turno':turno_id,'formato':formato}),
        'promociones' : VentasPorTurnoResumenPromociones({'turno':turno_id,'formato':formato}),
        'devoluciones' : VentasPorTurnoResumenDevoluciones({'turno':turno_id,'formato':formato}),
        'stock_critico' : VentasPorTurnoResumenStockCritico({'turno':turno_id,'formato':formato})
    }[resumen]
    return reporte.get_response()

@staff_member_required
def ventas_mes(request):
    """Vista que genera un reporte de producto"""
    if request.method == 'POST': 
        form = VentaMesForm(request.session['anios'],request.session['hoy'],request.POST)
        if form.is_valid():
            if int(form.cleaned_data['tipo_reporte']) == VentaMesForm.REPORTE_DETALLE:
                return VentasPorMes(form.cleaned_data).get_response()
            else:
                return VentasPorMesResumido(form.cleaned_data).get_response()
    else:
        anios = Turno.objects.aggregate(fin=Max('fecha_apertura_sistema'),inicio=Min('fecha_apertura_sistema'))
        hoy = datetime.now()
        form = VentaMesForm(anios=anios,dia=hoy)
        request.session['hoy'] = hoy
        request.session['anios'] = anios
    return render_to_response('reporte/venta_mes.html', {
        'form': form,
    },context_instance=RequestContext(request))

@staff_member_required
def ventas_graficos_periodo_categoria(request):
    """Vista que genera un reporte de producto"""
    if request.method == 'POST': 
        form = VentasGraficosPorCategoriaForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data.get('elemento')
            if int(form.cleaned_data['categoria']) == VentasGraficosPorCategoriaForm.TODAS_LAS_CATEGORIAS:
                if tipo == u'1':
                    return VentasGraficoProducto(form.cleaned_data).get_response()
                elif tipo == u'2':
                    return VentasGraficoPromocion(form.cleaned_data).get_response()
            else:
                if tipo == u'1':
                    return VentasGraficoProductoPorCategoria(form.cleaned_data).get_response()
                elif tipo == u'2':
                    return VentasGraficoPromocionPorCategoria(form.cleaned_data).get_response()
    else:
        form = VentasGraficosPorCategoriaForm()
    return render_to_response('reporte/venta_grafico_periodo_categoria.html', {
        'form': form,
    },context_instance=RequestContext(request))

@staff_member_required
def get_birt_img(request):
    rootPath = REPORT_IMAGE_DIR
    pattern = request.GET['__imageid']
    full_img_path = None
    for root, dirs, files in os.walk(rootPath):
        for filename in fnmatch.filter(files, pattern):
                full_img_path = os.path.join(root, filename)
    with file(full_img_path,'rb') as imgfile:
        imagedata = imgfile.read()
    return HttpResponse(imagedata, mimetype='image/png')