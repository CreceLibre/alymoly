#!/usr/bin/env python
#-*- encoding: UTF-8 -*-
###############################################
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@minostro.com                       #
# 2009                                        #
###############################################

import json
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from AlyMoly.venta.views import autentifacion_requerida, manejo_error, verificar_turno
from django.shortcuts import render_to_response
from AlyMoly.devolucion import clases, excepciones
from AlyMoly.venta import recursos, clases as venta_clases, excepciones as venta_excepciones
from AlyMoly.settings import DESCRIPCION_PROMOCION, DESCRIPCION_PRODUCTO, CANTIDAD_MAXIMA
from django.utils.translation import ugettext


def devolucion(a_request):
    verificar_turno(a_request)
    if a_request.user.is_authenticated():
        if not a_request.user.is_superuser and not a_request.user.is_staff:
            return render_to_response('index.html')
        else:
            if a_request.is_ajax():
                return HttpResponseBadRequest(u"No tiene privilegios para realizar esta acción.  Debe iniciar sesion nuevamente.")
            else:
                HttpResponseRedirect('/venta/')
    return HttpResponseRedirect('/venta/')


def nueva_devolucion(a_request):
    try:
        del(a_request.session['devolucion'])
        del(a_request.session['elemento'])
    except:
        pass


@autentifacion_requerida
@manejo_error
def cuerpo_devolucion(a_request):
    nueva_devolucion(a_request)
    a_request.session['devolucion'] = clases.Devolucion(fecha_devolucion=datetime.today(),turno=a_request.session['turno'])
    return render_to_response('cuerpo.html')

@autentifacion_requerida
@manejo_error
def buscar_elemento(a_request, codigo_barra_):
    try:
        elemento = venta_clases.Producto(codigo_barra=codigo_barra_,descripcion=DESCRIPCION_PRODUCTO)
        a_request.session['elemento'] = elemento
    except venta_excepciones.ProductoExistenciaError, a_mensaje:
        raise excepciones.ProductoExistenciaError(a_mensaje)
    except venta_excepciones.ProductoError, a_mensaje:
        try:
            elemento = venta_clases.Promocion(codigo=codigo_barra_,descripcion=DESCRIPCION_PROMOCION, descripcion_productos=DESCRIPCION_PRODUCTO)
            a_request.session['elemento'] = elemento
        except venta_excepciones.PromocionExistenciaError, a_mensaje:
            raise excepciones.PromocionExistenciaError(a_mensaje)
        except venta_excepciones.PromocionError, a_mensaje:
            raise venta_excepciones.PromocionError(u"Producto o Promoción asociado al código %s no existe"%(codigo_barra_))
        else:
            data = {'descripcion':elemento.get_descripcion(),'precio':recursos.formato_dinero(elemento.precio_venta)}
            a_request.session['elemento'] = elemento
            return HttpResponse(json.dumps(data),content_type="text/plain")
    else:
        data = {'descripcion':elemento.get_descripcion(),'precio':recursos.formato_dinero(elemento.precio_venta)}
        a_request.session['elemento'] = elemento
        return HttpResponse(json.dumps(data),content_type="text/plain")


@autentifacion_requerida
@manejo_error
def agregar_elemento(a_request, cantidad_):
    try:
        cantidad = int(cantidad_)
        if not cantidad > 0:
            raise Exception(u"Cantidad de producto debe ser un entero mayor a cero.")
        if cantidad > CANTIDAD_MAXIMA:
            raise Exception(u"Sólo puede agregar hasta %s productos por vez."%(CANTIDAD_MAXIMA))
    except ValueError:
        raise Exception("Cantidad de producto debe ser un entero mayor a cero.")
    elemento = a_request.session['elemento']
    devolucion = a_request.session['devolucion']
    linea_detalle = devolucion.add_linea_detalle(clases.LineaDetalle(devolucion,elemento, cantidad))
    a_request.session['devolucion'] = devolucion
    limpiar_elementos(a_request)
    elemento_data ={'descripcion':linea_detalle.get_descripcion(),
               'precio_venta':recursos.formato_dinero(linea_detalle.get_precio_unitario()),
               'cantidad':recursos.formato_miles(linea_detalle.get_cantidad()),
               'precio_total':recursos.formato_dinero(linea_detalle.get_precio_total()),
               'codigo':linea_detalle.get_codigo_barra()
               }
    data = {'elemento':elemento_data}
    return HttpResponse(json.dumps(data),content_type="text/plain")


@autentifacion_requerida
@manejo_error
def aumentar(a_request, codigo_barra_):
    devolucion = a_request.session['devolucion']
    linea_detalle = devolucion.aumentar_linea_detalle(codigo_barra_)
    a_request.session['devolucion'] = devolucion
    limpiar_elementos(a_request)
    elemento_data ={'descripcion':linea_detalle.get_descripcion(),
               'precio_venta':recursos.formato_dinero(linea_detalle.get_precio_unitario()),
               'cantidad':recursos.formato_miles(linea_detalle.get_cantidad()),
               'precio_total':recursos.formato_dinero(linea_detalle.get_precio_total()),
               'codigo':linea_detalle.get_codigo_barra()
               }
    data = {'elemento':elemento_data}
    return HttpResponse(json.dumps(data),content_type="text/plain")


@autentifacion_requerida
@manejo_error
def disminuir(a_request, codigo_barra_):
    devolucion = a_request.session['devolucion']
    linea_detalle = devolucion.disminuir_linea_detalle(codigo_barra_)
    a_request.session['devolucion'] = devolucion
    limpiar_elementos(a_request)
    elemento_data ={'descripcion':linea_detalle.get_descripcion(),
               'precio_venta':recursos.formato_dinero(linea_detalle.get_precio_unitario()),
               'cantidad':recursos.formato_miles(linea_detalle.get_cantidad()),
               'precio_total':recursos.formato_dinero(linea_detalle.get_precio_total()),
               'codigo':linea_detalle.get_codigo_barra()
               }
    data = {'elemento':elemento_data}
    return HttpResponse(json.dumps(data),content_type="text/plain")


@autentifacion_requerida
@manejo_error
def eliminar(a_request, codigo_barra_):
    devolucion = a_request.session['devolucion']
    devolucion.delete_linea_detalle(codigo_barra_)
    a_request.session['devolucion'] = devolucion
    limpiar_elementos(a_request)
    return HttpResponse()


def limpiar_elementos(a_request):
    try:
        del(a_request.session['elemento'])
    except:
        pass


@autentifacion_requerida
@manejo_error
def registrar(a_request):
    devolucion = a_request.session['devolucion']
    devolucion.save()
    a_request.session['turno'] = devolucion.turno
    return HttpResponse()

@autentifacion_requerida
@manejo_error
def cabecera(a_request):
    devolucion = a_request.session['devolucion']
    fecha = devolucion.fecha_devolucion.strftime("%A-%d-%B-%Y-%H:%M:%S").split('-')
    dia_semana = ugettext('%(day)s'%{'day':fecha[0]})
    mes = ugettext('%(month)s'%{'month':fecha[2]})
    data = {
            'fecha_devolucion':'%s %s %s %s - %s'%(dia_semana.capitalize(),fecha[1],mes.capitalize(),fecha[3],fecha[4])
            }
    return HttpResponse(json.dumps(data),content_type="text/plain")
