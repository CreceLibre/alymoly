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
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib import auth
from AlyMoly.venta import clases, forms, recursos, excepciones, models
from django.utils.translation import ugettext
from django.template import RequestContext
from AlyMoly.settings import ROOT, NOMBRE_SUCURSAL, DESCRIPCION_PROMOCION, \
    DESCRIPCION_PRODUCTO, CANTIDAD_MAXIMA, CANTIDAD_MAXIMA_PRODUCTOS


def autentifacion_requerida(a_funcion):
    def wrap(a_request, *args, **kwargs):
        if a_request.user.is_authenticated():
            if not a_request.user.is_superuser and not a_request.user.is_staff:
                return a_funcion(a_request, *args, **kwargs)
            else:
                if a_request.is_ajax():
                    #mensaje_ = u"No tiene privilegios para realizar esta acción.  Debe iniciar sesion nuevamente."
                    badrequest_ = HttpResponseBadRequest('')
                    badrequest_['inicio_sesion'] = json.dumps(True)
                    return badrequest_
                else:
                    return HttpResponseRedirect('/venta/')
        else:
            if a_request.is_ajax():
                #mensaje_ = u"Debe iniciar sesion nuevamente."
                badrequest_ = HttpResponseBadRequest('')
                badrequest_['inicio_sesion'] = json.dumps(True)
                return badrequest_
            else:
                return HttpResponseRedirect('/venta/')
    wrap.__doc__ = a_funcion.__doc__
    wrap.__name__ = a_funcion.__name__
    return wrap


def manejo_error(a_funcion):
    def wrap(a_request, *args, **kwargs):
        try:
            return a_funcion(a_request, *args, **kwargs)
        except Exception, a_mensaje:
            return HttpResponseBadRequest(u"%s" % a_mensaje)
    wrap.__doc__ = a_funcion.__doc__
    wrap.__name__ = a_funcion.__name__
    return wrap


def autentificacion(a_request):
    if a_request.method == 'POST':
        formulario_ = forms.AutentificacionForm(a_request.POST)
        if formulario_.is_valid():
            ci_, dv_ = recursos.get_ci_dv(
                formulario_.cleaned_data['cedula_identidad'])
            # problemas con el 0 para las personas menores a 10 millones
            ci_ = str(int(ci_))
            try:
                trabajador_ = clases.Trabajador(id=ci_ + "-" + dv_)
            except excepciones.TrabajadorError, a_mensaje:
                formulario_._errors['__all__'] = [a_mensaje]
                return render(a_request,'autentificacion.html', {'formulario': formulario_})
            user_ = auth.authenticate(username=ci_ + dv_, password=ci_ + dv_)
            if user_ is not None and user_.is_active and user_ == trabajador_.get_user():
                auth.login(a_request, user_)
            else:
                formulario_._errors['__all__'] = [
                    u"Su usuario de sistema no existe o no está activo."]
                return render(a_request,'autentificacion.html', {'formulario': formulario_})
            a_request.session['trabajador'] = trabajador_
            return HttpResponseRedirect('/venta/turno/abrir')
    else:
        formulario_ = forms.AutentificacionForm()
    return render(a_request,'autentificacion.html', {'formulario': formulario_})


def verificar_turno(a_request):
    if not 'turno' in a_request.session:
        return HttpResponseRedirect('/venta/')
    if not a_request.session['turno'].activo():
        auth.logout(a_request)
        return HttpResponseRedirect('/venta/')


@autentifacion_requerida
def turno_abrir(a_request):
    fecha_ = datetime.today()
    if a_request.method == "POST":
        #a_request.POST['trabajador'] = a_request.session['trabajador']
        formulario_ = forms.TurnoForm(a_request.POST)
        if formulario_.is_valid():
            argumentos_ = {
                'fecha_apertura_sistema': fecha_,
                'monto_apertura_caja': formulario_.cleaned_data['monto_apertura_caja'],
                'trabajador': a_request.session['trabajador']
            }
            try:
                turno_ = clases.Turno(**argumentos_)
                a_request.session['turno'] = turno_
                a_request.session['inicio_automatico'] = False
                return HttpResponseRedirect('/venta/venta/')
            except excepciones.TurnoError, a_mensaje:
                formulario_._errors['__all__'] = [
                    u"%s  Favor autentificarse nuevamente." % a_mensaje]
    else:
        a_request.session['inicio_automatico'] = True
        try:
            turno_ = clases.Turno(
                trabajador_id=a_request.session['trabajador'].id,
                descripcion_producto=DESCRIPCION_PRODUCTO,
                descripcion_promocion=DESCRIPCION_PROMOCION
            )
            a_request.session['turno'] = turno_
            return HttpResponseRedirect('/venta/venta/')
        except excepciones.TurnoError, a_mensaje:
            pass
        except excepciones.TurnoMultipleError, a_mensaje:
            raise excepciones.TurnoMultipleError(u"%s" % a_mensaje)
        formulario_ = forms.TurnoForm()
    return render(a_request, 'turno/turno.html',
                  {
                      'trabajador': a_request.session['trabajador'],
                      'formulario': formulario_,
                      'sucursal': NOMBRE_SUCURSAL},
                  )


def venta(a_request):
    verificar_turno(a_request)
    if a_request.user.is_authenticated():
        if not a_request.user.is_superuser and not a_request.user.is_staff:
            return render(a_request, 'venta/index.html',
                          {'inicio_automatico': a_request.session[
                              'inicio_automatico']}
                          )
        else:
            if a_request.is_ajax():
                #mensaje_ = u"No tiene privilegios para realizar esta acción.  Debe iniciar sesion nuevamente."
                badrequest_ = HttpResponseBadRequest('')
                badrequest_['inicio_sesion'] = json.dumps(True)
                return badrequest_
    return HttpResponseRedirect('/venta/')


def nueva_venta(a_request):
    verificar_turno(a_request)
    try:
        del(a_request.session['venta'])
        del(a_request.session['elemento'])
    except:
        pass
    """
        Se asume medio_pago --> 1, efectivo
    """
    a_request.session['venta'] = clases.Venta(
        fecha_venta=datetime.today(),
        turno=a_request.session['turno'],
        medio_pago=1,
        cantidad_elementos=CANTIDAD_MAXIMA_PRODUCTOS)


def limpiar_elementos(a_request):
    try:
        del(a_request.session['elemento'])
    except:
        pass


@autentifacion_requerida
def cuerpo_venta(a_request):
    verificar_turno(a_request)
    nueva_venta(a_request)
    return render(a_request, 'venta/cuerpo.html')


@autentifacion_requerida
@manejo_error
def buscar_elemento(a_request, codigo_barra_):
    verificar_turno(a_request)
    try:
        elemento = clases.Producto(
            verificar_existencia=True, codigo_barra=codigo_barra_, descripcion=DESCRIPCION_PRODUCTO)
        a_request.session['elemento'] = elemento
    except excepciones.ProductoExistenciaError, a_mensaje:
        badrequest = HttpResponseBadRequest(u"%s" % a_mensaje)
        badrequest['existencia_error'] = json.dumps(True)
        return badrequest
    except excepciones.ProductoError, a_mensaje:
        try:
            elemento = clases.Promocion(
                codigo=codigo_barra_,
                descripcion=DESCRIPCION_PROMOCION,
                descripcion_productos=DESCRIPCION_PRODUCTO,
                verificar_existencia=True)
            a_request.session['elemento'] = elemento
        except excepciones.PromocionExistenciaError, a_mensaje:
            badrequest = HttpResponseBadRequest(u"%s" % a_mensaje)
            badrequest['existencia_error'] = json.dumps(True)
            return badrequest
        except excepciones.PromocionError, a_mensaje:
            raise excepciones.PromocionError(
                u"Producto o Promoción asociado al código %s no existe" % (codigo_barra_))
        else:
            data = {'descripcion': elemento.get_descripcion(
            ), 'precio_venta': recursos.formato_dinero(elemento.precio_venta)}
            a_request.session['elemento'] = elemento
            return HttpResponse(json.dumps(data), content_type="text/plain")
    else:
        data = {'descripcion': elemento.get_descripcion(
        ), 'precio_venta': recursos.formato_dinero(elemento.precio_venta)}
        a_request.session['elemento'] = elemento
        return HttpResponse(json.dumps(data), content_type="text/plain")


@autentifacion_requerida
@manejo_error
def agregar_elemento(a_request, cantidad_):
    verificar_turno(a_request)
    try:
        cantidad = int(cantidad_)
        if not cantidad > 0:
            raise Exception(
                u"Cantidad de producto debe ser un entero mayor a cero.")
        if cantidad > CANTIDAD_MAXIMA:
            raise Exception(
                u"Sólo puede agregar hasta %s productos por vez." % (CANTIDAD_MAXIMA))
    except ValueError:
        raise Exception(
            "Cantidad de producto debe ser un entero mayor a cero.")
    elemento = a_request.session['elemento']
    venta = a_request.session['venta']
    linea_detalle = venta.add_linea_detalle(
        clases.LineaDetalle(especificacion=elemento, cantidad=cantidad))
    a_request.session['venta'] = venta
    limpiar_elementos(a_request)
    venta_data = {'total_afecto': recursos.formato_dinero(venta.monto_afecto),
                  'total_exento': recursos.formato_dinero(venta.monto_exento),
                  'monto_total': recursos.formato_dinero(venta.monto_total),
                  'total_productos': recursos.formato_miles(venta.cantidad_productos),
                  'ultimo_tipo_elemento': venta.ultimo_tipo_elemento
                  }
    elemento_data = {'descripcion': linea_detalle.get_descripcion(),
                     'precio_venta': recursos.formato_dinero(linea_detalle.get_precio_unitario()),
                     'cantidad': recursos.formato_miles(linea_detalle.get_cantidad()),
                     'precio_total': recursos.formato_dinero(linea_detalle.get_precio_total()),
                     'codigo': linea_detalle.get_codigo_barra().replace("*", "_")  # se cambia * por _
                     }
    componentes_data = []
    if venta.ultimo_tipo_elemento == 1:
        for elemento_ in elemento.componentes:
            componentes_data.append(
                [elemento_.cantidad_compone, elemento_.get_descripcion()])
    elif venta.ultimo_tipo_elemento == 2:
        for elemento_ in elemento.productos:
            componentes_data.append(elemento_.get_descripcion())
    data = {'venta': venta_data,
            'elemento': elemento_data,
            'componentes': componentes_data
            }
    return HttpResponse(json.dumps(data), content_type="text/plain")


@autentifacion_requerida
@manejo_error
def aumentar(a_request, codigo_barra_):
    verificar_turno(a_request)
    venta = a_request.session['venta']
    linea_detalle = venta.aumentar_linea_detalle(
        codigo_barra_.replace('_', '*'))  # se transforma a codificacion interna
    a_request.session['venta'] = venta
    venta_data = {'total_afecto': recursos.formato_dinero(venta.monto_afecto),
                  'total_exento': recursos.formato_dinero(venta.monto_exento),
                  'monto_total': recursos.formato_dinero(venta.monto_total),
                  'total_productos': recursos.formato_miles(venta.cantidad_productos),
                  }
    elemento_data = {'descripcion': linea_detalle.get_descripcion(),
                     'precio_venta': recursos.formato_dinero(linea_detalle.get_precio_unitario()),
                     'cantidad': recursos.formato_miles(linea_detalle.get_cantidad()),
                     'precio_total': recursos.formato_dinero(linea_detalle.get_precio_total()),
                     'codigo': linea_detalle.get_codigo_barra().replace('*', '_')
                     }
    data = {'venta': venta_data,
            'elemento': elemento_data
            }
    return HttpResponse(json.dumps(data), content_type="text/plain")


@autentifacion_requerida
@manejo_error
def disminuir(a_request, codigo_barra_):
    verificar_turno(a_request)
    venta = a_request.session['venta']
    linea_detalle = venta.disminuir_linea_detalle(
        codigo_barra_.replace('_', '*'))
    a_request.session['venta'] = venta
    venta_data = {'total_afecto': recursos.formato_dinero(venta.monto_afecto),
                  'total_exento': recursos.formato_dinero(venta.monto_exento),
                  'monto_total': recursos.formato_dinero(venta.monto_total),
                  'total_productos': recursos.formato_miles(venta.cantidad_productos),
                  }
    elemento_data = {'descripcion': linea_detalle.get_descripcion(),
                     'precio_venta': recursos.formato_dinero(linea_detalle.get_precio_unitario()),
                     'cantidad': recursos.formato_miles(linea_detalle.get_cantidad()),
                     'precio_total': recursos.formato_dinero(linea_detalle.get_precio_total()),
                     'codigo': linea_detalle.get_codigo_barra().replace('*', '_')
                     }
    data = {'venta': venta_data,
            'elemento': elemento_data
            }
    return HttpResponse(json.dumps(data), content_type="text/plain")


@autentifacion_requerida
@manejo_error
def eliminar(a_request, codigo_barra_):
    verificar_turno(a_request)
    venta = a_request.session['venta']
    venta.delete_linea_detalle(codigo_barra_.replace('_', '*'))
    a_request.session['venta'] = venta
    venta_data = {'total_afecto': recursos.formato_dinero(venta.monto_afecto),
                  'total_exento': recursos.formato_dinero(venta.monto_exento),
                  'monto_total': recursos.formato_dinero(venta.monto_total),
                  'total_productos': recursos.formato_miles(venta.cantidad_productos),
                  }
    data = {'venta': venta_data
            }
    return HttpResponse(json.dumps(data), content_type="text/plain")


@autentifacion_requerida
@manejo_error
def medio_pago(a_request, medio_):
    verificar_turno(a_request)
    venta_ = a_request.session['venta']
    venta_.set_medio_pago(int(medio_))
    a_request.session['venta'] = venta_
    return HttpResponse()


@autentifacion_requerida
@manejo_error
def calcular_vuelto(a_request, cantidad_):
    verificar_turno(a_request)
    try:
        cantidad = int(cantidad_)
    except ValueError:
        data = {'cantidad_correcta': False,
                'total_vuelto': recursos.formato_dinero(0)}
        return HttpResponse(json.dumps(data), content_type="text/plain")
    total_vuelto = cantidad - a_request.session['venta'].monto_total
    cantidad_correcta = True
    if total_vuelto < 0:
        cantidad_correcta = False
    data = {'cantidad_correcta': cantidad_correcta,
            'total_vuelto': recursos.formato_dinero(total_vuelto)}
    return HttpResponse(json.dumps(data), content_type="text/plain")


@autentifacion_requerida
@manejo_error
def registrar_venta(a_request):
    verificar_turno(a_request)
    venta = a_request.session['venta']
    venta.save()
    turno = venta.turno
    turno.ultima_venta = venta
    a_request.session['turno'] = turno
    nueva_venta(a_request)
    venta = a_request.session['venta']
    fecha = venta.fecha_venta.strftime("%A-%d-%B-%Y-%H:%M:%S").split('-')
    dia_semana = ugettext('%(day)s' % {'day': fecha[0]})
    mes = ugettext('%(month)s' % {'month': fecha[2]})
    venta_data = {'total_afecto': recursos.formato_dinero(venta.monto_afecto),
                  'total_exento': recursos.formato_dinero(venta.monto_exento),
                  'monto_total': recursos.formato_dinero(venta.monto_total),
                  'total_productos': recursos.formato_miles(venta.cantidad_productos),
                  'fecha_venta': '%s %s %s %s - %s' % (
        dia_semana.capitalize(),
        fecha[1],
        mes.capitalize(),
        fecha[3],
        fecha[4])
    }
    data = {
        'venta': venta_data,
        'ultima_venta': construir_ultima_venta(turno)
    }
    return HttpResponse(json.dumps(data), content_type="text/plain")


@autentifacion_requerida
@manejo_error
def cabecera(a_request):
    verificar_turno(a_request)
    turno = a_request.session['turno']
    fecha = turno.get_fecha_apertura_sistema().strftime(
        "%A-%d-%B-%Y-%H:%M:%S").split('-')
    dia_semana = ugettext('%(day)s' % {'day': fecha[0]})
    mes = ugettext('%(month)s' % {'month': fecha[2]})
    turno_data = {'trabajador': turno.trabajador.get_nombre_completo(),
                  'sucursal': NOMBRE_SUCURSAL,
                  'fecha_apertura_sistema': '%s %s %s %s - %s' % (dia_semana.capitalize(), fecha[1], mes.capitalize(), fecha[3], fecha[4])}
    venta = a_request.session['venta']
    fecha = venta.fecha_venta.strftime("%A-%d-%B-%Y-%H:%M:%S").split('-')
    dia_semana = ugettext('%(day)s' % {'day': fecha[0]})
    mes = ugettext('%(month)s' % {'month': fecha[2]})
    venta_data = {
        'fecha_venta': '%s %s %s %s - %s' % (dia_semana.capitalize(), fecha[1], mes.capitalize(), fecha[3], fecha[4])
    }
    ultima_venta_data = None
    if turno.ultima_venta is not None:
        ultima_venta_data = construir_ultima_venta(turno)
    data = {'turno': turno_data,
            'venta': venta_data,
            'ultima_venta': ultima_venta_data}
    return HttpResponse(json.dumps(data), content_type="text/plain")


@autentifacion_requerida
@manejo_error
def turno_cerrar(a_request):
    verificar_turno(a_request)
    fecha_ = datetime.today()
    if a_request.method == "POST":
        try:
            instance_ = a_request.session['turno'].get_orm()
        except:
            return HttpResponseRedirect('/venta/')
        formulario_ = forms.CerrarTurnoForm(a_request.POST, instance=instance_)
        formulario_deposito_ = forms.BoletaDepositoForm(a_request.POST)
        if formulario_.is_valid() and formulario_deposito_.is_valid():
            try:
                turno_ = a_request.session['turno']
                turno_.cerrar(fecha_cierre_sistema=fecha_,
                              boleta_deposito=formulario_deposito_)
                auth.logout(a_request)
                return HttpResponseRedirect('/venta/turno/cerrado/%s/' % turno_.id)
            except Exception, a_mensaje:
                raise Exception(
                    "Problemas para cerrar el turno. %s" % a_mensaje)
    else:
        formulario_ = forms.CerrarTurnoForm()
        formulario_deposito_ = forms.BoletaDepositoForm()
    return render(a_request, "turno/cierre_turno.html",
                  {'formulario': formulario_,
                   'formulario_deposito': formulario_deposito_,
                   'turno': a_request.session['turno']}
                  )


def confeccionar_boleta(**kwargs):
    boleta_img_ = Image.open(
        ROOT('media/static/images/venta/boleta_deposito.png'))
    boleta_draw_ = ImageDraw.Draw(boleta_img_)
    #font = ImageFont.load_default()
    font = ImageFont.truetype(ROOT('media/static/fonts/Calibri.ttf'), 40)
    boleta_draw_.text((70, 290), kwargs['sucursal'], fill='black', font=font)
    boleta_draw_.text((70, 490), kwargs['trabajador'], fill='black', font=font)
    boleta_draw_.text((980, 290), kwargs['fecha'], fill='black', font=font)
    boleta_draw_.text((965, 490), kwargs['turno'], fill='black', font=font)
    # detalle de monto_total_turno
    MARGEN_DERECHO = 2150
    MARGEN_SUPERIOR = 110
    boleta_ = kwargs['boleta_deposito']
    texto = recursos.formato_dinero(boleta_.veintemil)
    boleta_draw_.text((MARGEN_DERECHO - font.getsize(texto)
                       [0], MARGEN_SUPERIOR), texto, fill='black', font=font)
    MARGEN_SUPERIOR += 60
    texto = recursos.formato_dinero(boleta_.diezmil)
    boleta_draw_.text((MARGEN_DERECHO - font.getsize(texto)
                       [0], MARGEN_SUPERIOR), texto, fill='black', font=font)
    MARGEN_SUPERIOR += 60
    texto = recursos.formato_dinero(boleta_.cincomil)
    boleta_draw_.text((MARGEN_DERECHO - font.getsize(texto)
                       [0], MARGEN_SUPERIOR), texto, fill='black', font=font)
    MARGEN_SUPERIOR += 60
    texto = recursos.formato_dinero(boleta_.dosmil)
    boleta_draw_.text((MARGEN_DERECHO - font.getsize(texto)
                       [0], MARGEN_SUPERIOR), texto, fill='black', font=font)
    MARGEN_SUPERIOR += 60
    texto = recursos.formato_dinero(boleta_.mil)
    boleta_draw_.text((MARGEN_DERECHO - font.getsize(texto)
                       [0], MARGEN_SUPERIOR), texto, fill='black', font=font)
    MARGEN_SUPERIOR += 60
    texto = recursos.formato_dinero(boleta_.quinientos)
    boleta_draw_.text((MARGEN_DERECHO - font.getsize(texto)
                       [0], MARGEN_SUPERIOR), texto, fill='black', font=font)
    MARGEN_SUPERIOR += 60
    texto = recursos.formato_dinero(boleta_.cien)
    boleta_draw_.text((MARGEN_DERECHO - font.getsize(texto)
                       [0], MARGEN_SUPERIOR), texto, fill='black', font=font)
    MARGEN_SUPERIOR += 60
    texto = recursos.formato_dinero(boleta_.cincuenta)
    boleta_draw_.text((MARGEN_DERECHO - font.getsize(texto)
                       [0], MARGEN_SUPERIOR), texto, fill='black', font=font)
    MARGEN_SUPERIOR += 60
    texto = recursos.formato_dinero(boleta_.diez)
    boleta_draw_.text((MARGEN_DERECHO - font.getsize(texto)
                       [0], MARGEN_SUPERIOR), texto, fill='black', font=font)
    MARGEN_SUPERIOR += 60
    texto = recursos.formato_dinero(boleta_.tarjetas)
    boleta_draw_.text((MARGEN_DERECHO - font.getsize(texto)
                       [0], MARGEN_SUPERIOR), texto, fill='black', font=font)
    MARGEN_SUPERIOR += 60
    texto = recursos.formato_dinero(boleta_.otros)
    boleta_draw_.text((MARGEN_DERECHO - font.getsize(texto)
                       [0], MARGEN_SUPERIOR), texto, fill='black', font=font)
    MARGEN_SUPERIOR += 60
    texto = recursos.formato_dinero(boleta_.total)
    boleta_draw_.text((MARGEN_DERECHO - font.getsize(texto)
                       [0], MARGEN_SUPERIOR), texto, fill='black', font=font)
    return boleta_img_


def boleta_deposito(a_request, a_id):
    try:
        turno_ = clases.Turno(id=int(a_id))
        if turno_.estado == 1:
            raise excepciones.TurnoError(
                u"Turno debe estar cerrado para consultar su boleta de deposito.")
        boleta_deposito_ = models.BoletaDeposito.objects.get(turno=turno_.id)
    except Exception, a_mensaje:
        raise Exception("No se pudo generar Boleta de Deposito %s" % a_mensaje)
    datos = {}
    datos['sucursal'] = NOMBRE_SUCURSAL.upper()
    datos['fecha'] = turno_.fecha_apertura_sistema.strftime(
        "%d/%m/%Y") + ' - ' + turno_.fecha_cierre_sistema.strftime("%d/%m/%Y")
    datos['trabajador'] = turno_.trabajador.get_nombre_completo().upper()
    datos['turno'] = turno_.fecha_apertura_sistema.strftime("%H:%M:%S %p").lower(
    ) + ' - ' + turno_.fecha_cierre_sistema.strftime("%H:%M:%S %p").lower()
    datos['monto_total'] = turno_.get_monto_cierre_calculado()
    datos['boleta_deposito'] = boleta_deposito_
    boleta_src_ = confeccionar_boleta(**datos)
    response_ = HttpResponse(content_type='image/png')
    boleta_src_.save(response_, 'PNG')
    return response_


def turno_cerrado(a_request, a_id):
    return render(a_request,"turno/turno_cerrado.html", {'id': a_id})


def construir_ultima_venta(turno_):
    elementos_ultima_venta_data = []
    for linea_detalle in turno_.ultima_venta.linea_detalle.values():
        elementos_ultima_venta_data.append({
            'descripcion': linea_detalle.get_descripcion(),
            'precio_venta': recursos.formato_dinero(linea_detalle.get_precio_unitario()),
            'cantidad': recursos.formato_miles(linea_detalle.get_cantidad()),
            'precio_total': recursos.formato_dinero(linea_detalle.get_precio_total()),
            'codigo': linea_detalle.get_codigo_barra()
        })
    ultima_venta_data = {'monto_total': recursos.formato_dinero(turno_.ultima_venta.monto_total),
                         'total_productos': recursos.formato_miles(turno_.ultima_venta.cantidad_productos),
                         'elementos': elementos_ultima_venta_data
                         }
    return ultima_venta_data
