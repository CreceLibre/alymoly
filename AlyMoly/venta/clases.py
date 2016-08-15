#!/usr/bin/env python
#-*- encoding: UTF-8 -*-
from AlyMoly.venta.excepciones import TurnoError

###############################################
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@crecelibre.cl                      #
# 2009                                        #
###############################################

from django.db import transaction
from django.db.models import Sum
from AlyMoly.venta import models
from AlyMoly.mantenedor import models as mantenedor_models
from AlyMoly.movimiento import models as movimiento_models
from AlyMoly.devolucion import models as devolucion_models
from AlyMoly.venta.recursos import formato_dinero
from AlyMoly.venta.excepciones import *


class Trabajador(object):

    def __new__(cls, **kwargs):
        self_ = super(Trabajador,cls).__new__(cls)
        self_._orm = None
        if len(kwargs) == 0:
            return self_
        id_ = kwargs.get('id')
        if id_ is None:
            return self_
        try:
            ci_, dv_ = self_.get_ci_dv(id_)
        except:
            raise TrabajadorError(u"Cedula de identidad debe contener el separador (-) del digito verificador")
        try:
            self_._orm = models.Trabajador.objects.get(cedula_identidad=ci_,digito_verificador=dv_)
        except models.Trabajador.DoesNotExist:
            raise TrabajadorError(u'No existe trabajador')
        except Exception, a_mensaje:
            raise Exception(a_mensaje)
        return self_

    def __init__(self, **kwargs):
        self.cedula_identidad = self._orm.cedula_identidad
        self.digito_verificador = self._orm.digito_verificador
        self.nombre = self._orm.nombre
        self.apellido_paterno = self._orm.apellido_paterno
        self.apellido_materno = self._orm.apellido_materno
        self._user = self._orm.user

    def get_ci_dv(self, a_cedula):
        """
            Metodo que retorna la cédula de identidad separada por ci y dv
        """
        return a_cedula.split('-')

    def get_user(self):
        return self._user

    user = property(get_user)

    def get_id(self):
        return self._orm.id

    id = property(get_id)

    def get_nombre_completo(self):
        return u" ".join(elemento_ for elemento_ in (self.nombre,
                         self.apellido_paterno,
                         self.apellido_materno)
                         )

    def get_cedula_identidad(self):
        return str(self.cedula_identidad) + "-" + str(self.digito_verificador)


class Turno(object):
    ABIERTO = 1
    CERRADO = 2

    def __new__(cls, **kwargs):
        self_ = super(Turno,cls).__new__(cls)
        self_._orm = None
        if len(kwargs) == 0:
            return self_
        id_ = kwargs.get('id')
        if not id_ is None:
            try:
                self_._orm = models.Turno.objects.get(id=id_)
            except models.Turno.DoesNotExist:
                raise TurnoError(u"Turno con identificador %s no existe."%id_)
        trabajador_id = kwargs.get('trabajador_id')
        if not trabajador_id is None:
            try:
                self_._orm = models.Turno.objects.get(trabajador=trabajador_id, estado=1)
            except models.Turno.DoesNotExist:
                raise TurnoError(u"Turno asociado con este trabajador %s no existe."%id_)
            except models.Turno.MultipleObjectsReturned:
                raise TurnoMultipleError(u"Trabajador tiene abierto más de un turno, comuníquese con su administrador.")
        return self_

    def __init__(self, **kwargs):
        if kwargs.has_key('id') or kwargs.has_key('trabajador_id'):
            self.fecha_apertura_sistema = self._orm.fecha_apertura_sistema
            self.fecha_cierre_sistema = self._orm.fecha_cierre_sistema
            self._estado = self._orm.estado
            self._trabajador = Trabajador(id=self._orm.trabajador.get_cedula_identidad())
            self.monto_apertura_caja = self._orm.monto_apertura_caja
            self.monto_cierre_calculado = self._orm.monto_cierre_calculado
            self.monto_afecto = self._orm.monto_afecto
            self.monto_exento = self._orm.monto_exento
            if kwargs.has_key('descripcion_producto') is not False and kwargs.has_key('descripcion_promocion') is not False:
                try:
                    self._ultima_venta = Venta(
                                               id_turno = self.id,
                                               turno=self,
                                               descripcion_producto=kwargs['descripcion_producto'],
                                               descripcion_promocion=kwargs['descripcion_promocion']
                                               )
                except VentaNoExisteError:
                    self._ultima_venta = None
        else:
            """
                La responsabilidad de consolidar el nuevo objeto en la base de
                datos es del método abrir.
            """
            self.fecha_apertura_sistema = kwargs['fecha_apertura_sistema']
            self._estado = self.ABIERTO
            if not type(kwargs['trabajador']) is Trabajador:
                raise TurnoError(u'Debe especificar un trabajador')
            self._trabajador = kwargs['trabajador']
            self.monto_apertura_caja = kwargs['monto_apertura_caja']
            self.monto_afecto = 0
            self.monto_exento = 0
            self.monto_cierre_calculado = 0
            self.estado_sincronizacion = 1
            self._ultima_venta = None
            self.abrir()

    def get_trabajador(self):
        return self._trabajador

    trabajador = property(get_trabajador)

    def get_estado(self):
        return self._estado

    estado = property(get_estado)

    def get_ultima_venta(self):
        return self._ultima_venta

    def set_ultima_venta(self, venta_):
        self._ultima_venta = venta_

    ultima_venta = property(get_ultima_venta, set_ultima_venta)

    def abrir(self, **kwargs):
        """
            Se abre un turno, registrándolo en la base de datos.
        """
        if self._orm is not None:
            raise TurnoError('No es posible abrir Turno nuevamente.')
        try:
            models.Turno.objects.get(trabajador=self.trabajador.id, estado=1)
            raise TurnoError(u"Trabajador ya tiene un tierno abierto.")
        except models.Turno.DoesNotExist:
            try:
                self._orm = models.Turno()
                self._orm.__dict__.update(self.__dict__)
                self._orm.trabajador_id = self._trabajador.id
                self._orm.estado = self._estado
                self._orm.save()
            except Exception, a_mensaje:
                raise TurnoError(a_mensaje)

    @transaction.atomic
    def cerrar(self, **kwargs):
        """
            Se cierra el turno debido a que el trabajador ha finalizado su
            jornada laboral.
        """
        if not self._orm.estado == 1:
            raise TurnoError(u'No puede cerrar este turno, ya que no se encuentra abierto.')
        try:
            self._orm.fecha_cierre_sistema = self.fecha_cierre_sistema = kwargs['fecha_cierre_sistema']
            self._orm.estado = self._estado = self.CERRADO
            self._orm.save()
            boleta_deposito_ = kwargs['boleta_deposito']
            boleta_orm_ = boleta_deposito_.save(commit=False)
            boleta_orm_.turno_id = self._orm.id
            boleta_orm_.save()
        except Exception, a_mensaje:
            raise TurnoError(a_mensaje)

    def actualizar(self, **kwargs):
        """
            Método utilizado para actualizar determinados datos del turno.
        """
        try:
            self._orm.__dict__.update(kwargs)
            self._orm.save()
        except Exception, a_mensaje:
            raise TurnoError(a_mensaje)

    def aumentar_totales(self, a_total_venta, a_total_afecto, a_total_exento):
        """
            Método utilizado para aumentar los totales registrados en el turno.
            Este método generalmente es llamado al momento que una venta se
            ha consolidado en la base de datos.
        """
        dict_ = {'monto_cierre_calculado':self.monto_cierre_calculado + a_total_venta,
         'monto_afecto':self.monto_afecto + a_total_afecto,
         'monto_exento':self.monto_exento + a_total_exento
         }
        self.__dict__.update(dict_)
        self.actualizar(**dict_)

    def disminuir_totales(self, a_total_devolucion, a_total_afecto, a_total_exento):
        """
            Método utilizado para disminuir los totales registrados en el turno.
            Este método generalmente es llamado al momento que una anulación de
            venta se ha consolidado en la base de datos.
        """
        dict_ = {'monto_cierre_calculado':self.monto_cierre_calculado - a_total_devolucion,
         'monto_afecto':self.monto_afecto - a_total_afecto,
         'monto_exento':self.monto_exento - a_total_exento
         }
        self.__dict__.update(dict_)
        self.actualizar(**dict_)

    def get_fecha_apertura_sistema(self):
        return self.fecha_apertura_sistema

    def get_id(self):
        return self._orm.id

    id = property(get_id)

    def get_orm(self):
        self._orm

    def get_monto_cierre_calculado(self):
        return self.monto_cierre_calculado

    def activo(self):
        turno_ = models.Turno.objects.get(id=self.id)
        if turno_.estado == 2:
            return False
        return True



class Venta(object):

    def __new__(cls, **kwargs):
        self_ = super(Venta,cls).__new__(cls)
        self_._orm = None
        if len(kwargs) == 0:
            return self_
        id_turno = kwargs.get('id_turno')
        if not id_turno is None:
            try:
                self_._orm = models.Venta.objects.order_by('-id').filter(turno__pk=id_turno)[0]
            except IndexError:
                raise VentaNoExisteError()
        return self_

    def __init__(self, **kwargs):
        if kwargs.has_key('id_turno'):
            self.fecha_venta = self._orm.fecha_venta
            self.folio_boleta = self._orm.folio_boleta
            self._monto_total = self._orm.monto_total
            self.monto_afecto = self._orm.monto_afecto
            self.monto_exento = self._orm.monto_exento
            self.cantidad_productos = self._orm.cantidad_productos
            self.medio_pago = self._orm.medio_pago
            self.monto_pago = self._orm.monto_pago
            self._turno = kwargs['turno']
            self._ultimo_tipo_elemento = 0
            self._linea_detalle = {}
            self.set_linea_detalle(**kwargs)
        else:
            self.fecha_venta = kwargs['fecha_venta']
            self.folio_boleta = 0
            self._monto_total = 0
            self.monto_afecto = 0
            self.monto_exento = 0
            self.cantidad_productos = 0
            self.medio_pago = kwargs['medio_pago']
            self.monto_pago = None
            self._turno = kwargs['turno']
            self._ultimo_tipo_elemento = 0
            self._CANTIDAD_MAXIMA_ELEMENTOS = kwargs['cantidad_elementos']
            self._linea_detalle = {}

    def add_linea_detalle(self, a_linea):
        linea_detalle = a_linea
        codigo_ = a_linea.get_codigo_barra()
        if codigo_ in self._linea_detalle:
            """
                Código ya se encuentra en el detalle de la venta, se aumenta
                la cantidad solicitada de la linea de detalle existente.
            """
            try:
                linea_detalle_ = self._linea_detalle[codigo_]
                linea_detalle_.cantidad += linea_detalle.cantidad
                linea_detalle = linea_detalle_
            except Exception, a_mensaje:
                raise VentaError(a_mensaje)
        else:
            if len(self._linea_detalle) >= self._CANTIDAD_MAXIMA_ELEMENTOS:
                raise VentaError(u"No  puede agregar más de %s elementos diferentes"%self._CANTIDAD_MAXIMA_ELEMENTOS)
            self._linea_detalle[codigo_] = linea_detalle
        self.set_tipo_elemento(linea_detalle)
        self.calcular_totales()
        return linea_detalle

    def get_linea_detalle(self):
        return self._linea_detalle

    def set_linea_detalle(self,**kwargs):
        if self._orm is None:
            return
        for linea_detalle in models.LineaDetalle.objects.filter(venta__pk=self._orm.id):
            elemento = LineaDetalle(
                                    orm=linea_detalle,
                                    descripcion_producto=kwargs['descripcion_producto'],
                                    descripcion_promocion=kwargs['descripcion_promocion']
                                    )
            self._linea_detalle[elemento.get_codigo_barra()] = elemento

    linea_detalle = property(get_linea_detalle, add_linea_detalle)

    def delete_linea_detalle(self, a_codigo):
        try:
            self._linea_detalle.pop(a_codigo)
            self.calcular_totales()
        except KeyError:
            pass

    def get_tipo_elemento(self):
        return self._ultimo_tipo_elemento

    def set_tipo_elemento(self, a_linea):
        tipo = a_linea.get_tipo()
        if tipo is Promocion:
            self._ultimo_tipo_elemento = 2
        else:
            elemento = a_linea.get_especificacion()
            if elemento.producto_compuesto():
                self._ultimo_tipo_elemento = 1
            else:
                self._ultimo_tipo_elemento = 0

    ultimo_tipo_elemento = property(get_tipo_elemento,set_tipo_elemento)

    def aumentar_linea_detalle(self, a_codigo):
        try:
            linea_detalle_ = self.linea_detalle[a_codigo]
            linea_detalle_.cantidad += 1
            self.calcular_totales()
            return linea_detalle_
        except Exception, a_mensaje:
            raise VentaError(a_mensaje)

    def disminuir_linea_detalle(self, a_codigo):
        try:
            linea_detalle_ = self.linea_detalle[a_codigo]
            linea_detalle_.cantidad -= 1
            self.calcular_totales()
            return linea_detalle_
        except Exception, a_mensaje:
            raise VentaError(a_mensaje)

    def calcular_totales(self):
        self.reiniciar_valores()
        for linea_ in self._linea_detalle.values():
            self.calcular_total_productos(linea_.cantidad)
            if linea_.get_especificacion().get_exento_iva():
                self.calcular_exento(linea_.precio_total)
            else:
                self.calcular_afecto(linea_.precio_total)
        self.calcular_total_venta()

    def reiniciar_valores(self):
        self._monto_total = 0
        self.monto_afecto = 0
        self.monto_exento = 0
        self.cantidad_productos = 0

    def calcular_exento(self, a_precio):
        self.monto_exento += a_precio

    def calcular_afecto(self, a_precio):
        self.monto_afecto += a_precio

    def calcular_total_venta(self):
        self._monto_total = self.monto_afecto + self.monto_exento

    @transaction.atomic
    def save(self):
        """
            Método para concretar una venta.  Los pasos a seguir son:
            1.- Verificar que la venta cumpla con los requisitos
            mínimos para ser guardada.
            2.- Guardar la venta en la base de datos
            3.- Guardar todo el detalle de la venta en la base de datos
            4.- Aumentar totales en la caja.

            Es importante señalar que los puntos 2 y 3 deben realizarse dentro
            de una transacción de base de datos.
        """
        self.verificar_operacion()
        self._orm = models.Venta()
        self._orm.__dict__.update(
        {
         'monto_exento': self.monto_exento,
         'monto_total': self._monto_total,
         'folio_boleta': self.folio_boleta,
         'fecha_venta': self.fecha_venta,
         'cantidad_productos': self.cantidad_productos,
         'monto_afecto': self.monto_afecto,
         'medio_pago':self.medio_pago,
         'monto_pago':self.monto_pago,
         'turno_id': self._turno.id
         }
        )
        try:
            self._orm.save()
            for linea_detalle_ in self._linea_detalle.values():
                linea_detalle_.save(self._orm.id)
            self._turno.aumentar_totales(self._monto_total,self.monto_afecto,self.monto_exento)
        except Exception, a_mensaje:
            raise VentaError(a_mensaje)

    def set_medio_pago(self, a_medio_pago):
        self.medio_pago = int(a_medio_pago)

    def get_monto_total(self):
        return self._monto_total

    def set_monto_total(self, a_total):
        self._monto_total = a_total

    monto_total = property(get_monto_total, set_monto_total)

    def set_monto_pago(self, a_monto):
        self.monto_pago = a_monto

    def get_monto_pago(self, a_monto):
        return self.monto_pago

    def verificar_operacion(self):
        if len(self._linea_detalle) == 0:
            raise VentaError(u"Esta venta debe tener al menos un producto o promoción.")
        if not self.turno.activo():
            raise VentaError(u"Turno en estado cerrado, favor inicie nuevamente sesión.")

    def get_promociones(self):
        """
            Método utilizado para ayudar al usuario a saber de que otras
            existencias componen a la promoción actual.  Sólo
            utilizado en la IU.
        """
        promociones_ = []
        for linea_ in self.linea_detalle.values():
            if linea_.get_especificacion().__class__ is Promocion:
                promociones_.append(linea_)
        return promociones_

    def get_productos_compuestos(self):
        """
            Método utilizado para ayudar al usuario a saber de que otras
            existencias está compuesta la existencia actual.  Sólo
            utilizado en la IU.
        """
        productos_ = []
        for linea_ in self.linea_detalle.values():
            especificacion_ = linea_.get_especificacion()
            if especificacion_.__class__ is Producto and especificacion_.producto_compuesto():
                productos_.append(especificacion_)
        return productos_

    def get_linea_detalle_ui(self):
        return self._linea_detalle.values()

    def calcular_total_productos(self, a_cantidad):
        self.cantidad_productos += a_cantidad

    def get_turno(self):
        return self._turno

    turno = property(get_turno)


class LineaDetalle(object):

    def __new__(cls, **kwargs):
        self_ = super(LineaDetalle,cls).__new__(cls)
        self_._orm = None
        if len(kwargs) == 0:
            return self_
        orm = kwargs.get('orm')
        if not orm is None:
            self_._orm = orm
        return self_

    def __init__(self, **kwargs):
        if self._orm is None:
            self._especificacion_linea = kwargs['especificacion']
            self.cantidad = int(kwargs['cantidad'])
        else:
            self._especificacion_linea = Producto(
                                                  codigo_barra=self._orm.producto.codigo_barra,
                                                  descripcion=kwargs['descripcion_producto']
                                                  ) if self._orm.producto is not None else Promocion(
                                                                                                     codigo=self._orm.promocion.codigo,
                                                                                                     descripcion=kwargs['descripcion_promocion'],
                                                                                                     descripcion_productos=kwargs['descripcion_producto']
                                                                                                     )
            self._cantidad = self._orm.cantidad
            self.precio_venta = self._especificacion_linea.get_precio_unitario()
            self.precio_total = self._orm.precio_venta_total

    def get_cantidad(self):
        return self._cantidad

    def set_cantidad(self, a_cantidad):
        """
            Cada modificación que se realice en la cantidad requerida en la
            linea de detalle es auditada para verificar disponibilidad de
            la especificacion.
        """
        self._cantidad = a_cantidad
        self.existencia_suficiente(a_cantidad)
        self.calcular_total()

    cantidad = property(get_cantidad,set_cantidad)

    def calcular_total(self):
        self.precio_total = self.cantidad * self._especificacion_linea.get_precio_unitario()

    def get_precio_total(self):
        return self.precio_total

    def get_codigo_barra(self):
        return self._especificacion_linea.get_codigo_barra()

    def get_precio_unitario(self):
        return self._especificacion_linea.get_precio_unitario()

    def get_descripcion(self):
        return u'%s'%self._especificacion_linea.get_descripcion()

    def get_especificacion(self):
        return self._especificacion_linea

    @classmethod
    def get_factoria_especificacion(cls, a_clase, *args):
        try:
            return globals()[a_clase](*args)
        except KeyError:
            return FactoriaError("Clase hija no existe.")

    def existencia_suficiente(self, a_cantidad):
        self._especificacion_linea.verificar_existencia_requerida(a_cantidad)

    def get_tipo(self):
        return self._especificacion_linea.__class__

    def descontar_stock_actual(self):
        self._especificacion_linea.descontar_stock_actual(self._cantidad)

    def save(self, a_id_venta):
        """
            Método que guarda en base de datos la linea de detalle
            perteneciente a una venta relacionada con a_id_venta
        """
        datos_ = {
         'precio_venta_total': self.precio_total,
         'cantidad': self._cantidad,
         'venta_id': a_id_venta,
         'precio_venta': self.get_precio_unitario(),
         'promocion_id':None,
         'producto_id':None
        }
        if self.get_tipo() is Promocion:
            datos_.update({
             'promocion_id': self._especificacion_linea.get_orm().id
             }
            )
            self._orm = models.LineaDetalle()
            self._orm.__dict__.update(datos_)
            self._orm.save()
            self._especificacion_linea.descontar_stock_actual(self._cantidad)
        elif self.get_tipo() is Producto:
            datos_.update({
             'producto_id': self._especificacion_linea.get_orm().producto.id
             }
            )
            self._orm = models.LineaDetalle()
            self._orm.__dict__.update(datos_)
            self._orm.save()
            self.descontar_stock_actual()


class EspecificacionLinea(object):

    def __new__(cls, *args):
        if cls is EspecificacionLinea:
            raise AbstractaError(u"Clase abstracta, no se puede instanciar.")
        return object.__new__(cls)

    def __init__(self, a_descripcion):
        self.descripcion = a_descripcion

    def get_codigo_barra(self):
        pass

    def get_precio_unitario(self):
        pass

    def get_descripcion(self):
        pass

    def verificar_existencia_requerida(self, a_cantidad_requerida):
        pass

    def get_exento_iva(self):
        return False

    def get_bd_id(self):
        pass

    def save_elementos(self, a_linea_detalle):
        pass


class Producto(EspecificacionLinea):

    _instance = {}

    def __new__(cls, **kwargs):
        self_ = super(Producto,cls).__new__(cls)
        self_._orm = None
        if len(kwargs) == 0:
            return self_
        codigo = kwargs['codigo_barra']
        try:
            self_._orm = movimiento_models.ProductoBodega.objects.get(
                                                                      producto__codigo_barra=codigo,
                                                                      bodega__venta=True)
        except movimiento_models.ProductoBodega.DoesNotExist:
            raise ProductoError(u"El producto %s no esta asociado a su bodega de venta."%codigo)
        except Exception, a_mensaje:
            raise ProductoError(a_mensaje)
        return self_

    def __init__(self, verificar_existencia=False, **kwargs):
        self.codigo_barra = self._orm.producto.codigo_barra
        self._componentes = []
        self.set_descripcion(kwargs['descripcion'])
        self.precio_venta = self._orm.producto.precio_venta
        self.set_componentes(kwargs['descripcion'],verificar_existencia)
        if verificar_existencia:
            self.verificar_existencia_minima()
        self.nombre = self._orm.producto.nombre
        self.marca = self._orm.producto.marca
        self.tipo_envase = self._orm.producto.tipo_envase
        self.capacidad = self._orm.producto.capacidad
        self.exento_iva = self._orm.producto.exento_iva
        self.cantidad_compone = self._orm.producto.cantidad_compone
        self.stock_critico = self._orm.producto.stock_critico


    def get_orm(self):
        return self._orm

    orm  = property(get_orm)

    def set_descripcion(self, a_descripcion):
        descripcion_ = ""
        for campo_ in a_descripcion:
            if campo_ == 'precio_venta':
                descripcion_ += " " + u"%s"%formato_dinero(self._orm.producto.__dict__[campo_])
            else:
                descripcion_ += " " + u"%s"%self._orm.producto.__dict__[campo_]
        self.descripcion = descripcion_

    def get_descripcion(self):
        return u"" + self.descripcion

    def get_descripcion_excepcion(self):
        return u"%s %s"%(self.descripcion, formato_dinero(self.precio_venta))

    def get_id(self):
        return self._orm.id

    id = property(get_id)

    def get_stock_actual(self):
        _orm = movimiento_models.ProductoBodega.objects.get(producto__codigo_barra=self.codigo_barra, bodega__venta=True)
        return _orm.existencia

    stock_actual = property(get_stock_actual)

    def set_componentes(self, a_descripcion, verificar_existencia_):
        for producto_ in models.Producto.objects.filter(compone__codigo_barra=self.codigo_barra):
            self._componentes.append(Producto(verificar_existencia=verificar_existencia_,
                                              codigo_barra=producto_.codigo_barra,
                                              descripcion=a_descripcion))

    def get_componentes(self):
        return self._componentes

    componentes = property(get_componentes)

    def producto_compuesto(self):
        if len(self._componentes) == 0:
            return False
        return True

    def get_precio_unitario(self):
        return self.precio_venta

    def get_codigo_barra(self):
        return self.codigo_barra

    def verificar_existencia_minima(self):
        if not self.producto_compuesto() and self.stock_actual <= 0:
            raise ProductoExistenciaError(u"No hay stock disponible para vender %s."%self.get_descripcion_excepcion())

    def verificar_existencia_requerida(self, a_cantidad_requerida):
        if self.producto_compuesto():
            for producto_ in self._componentes:
                self.disponibilidad(producto_.stock_actual,a_cantidad_requerida,producto_.cantidad_compone)
        else:
            self.disponibilidad(self.stock_actual, a_cantidad_requerida)

    def disponibilidad(self, a_cantidad_actual, a_cantidad_requerida, a_multiplicador=1):
        """
            Método que calcula la diferencia que existe entre la cantidad de existencia real
            y la cantidad de existencia que se requiere, si no hay existencias suficientes
            se levanta una excepcion indicando esta situación.
        """
        if a_cantidad_actual - (a_cantidad_requerida * a_multiplicador) < 0:
            raise ProductoExistenciaError("No hay stock suficiente, solamente hay disponible %s"%(a_cantidad_actual/a_multiplicador))

    def get_exento_iva(self):
        return self.exento_iva

    def descontar_stock_actual(self, a_cantidad):
        """
            Método utilizado para poder descontar las existencias de la base de datos
        """
        self._orm = movimiento_models.ProductoBodega.objects.get(producto__codigo_barra=self.codigo_barra, bodega__venta=True)
        if self.producto_compuesto():
            for producto_ in self._componentes:
                producto_.descontar_stock_actual(producto_.cantidad_compone * a_cantidad)
        else:
            try:
                self._orm.existencia = self._orm.existencia - a_cantidad
                self._orm.save()
            except Exception, a_mensaje:
                raise ProductoDescuentoError(u"Error al descontar stock actual %s"%(a_mensaje))


    def aumentar_stock_actual(self, cantidad_):
        """
            Método utilizado para poder aumentar las existencias de la base de datos
        """
        self._orm = movimiento_models.ProductoBodega.objects.get(producto__codigo_barra=self.codigo_barra, bodega__venta=True)
        if self.producto_compuesto():
            for producto_ in self._componentes:
                producto_.aumentar_stock_actual(producto_.cantidad_compone * cantidad_)
        else:
            try:
                self._orm.existencia += cantidad_
                self._orm.save()
            except Exception, a_mensaje:
                raise ProductoAumentoError(u"Error al aumentar stock actual %s"%(a_mensaje))


    def get_cantidad_disponible_devolucion(self, turno_):
        """
            Método que retorna la cantidad de existencias que se han
            vendido con el turno indicado.
        """
        try:
            cantidad_vendida = models.LineaDetalle.objects.filter(
                                          producto__pk=self.orm.producto.id,
                                          venta__turno__pk=turno_.get_id()
                                          ).aggregate(cantidad=Sum('cantidad'))['cantidad']

            cantidad_devuelta = devolucion_models.Devolucion.objects.filter(
                                        producto__pk=self.orm.producto.id,
                                        turno__pk=turno_.get_id()
                                                ).aggregate(cantidad=Sum('cantidad_productos'))['cantidad']
        except:
            return ExistenciaError(u"Sucedió un problema calculando la cantidad vendida de la existencia.")
        else:
            cantidad_vendida = 0 if cantidad_vendida is None else cantidad_vendida
            cantidad_devuelta = 0 if cantidad_devuelta is None else cantidad_devuelta
            return cantidad_vendida - cantidad_devuelta


class Promocion(EspecificacionLinea):

    def __new__(cls, **kwargs):
        self_ = super(Promocion,cls).__new__(cls)
        self_._orm = None
        if len(kwargs) == 0:
            return self_
        try:
            self_._orm = models.Promocion.objects.get(codigo=kwargs['codigo'])
        except models.Promocion.DoesNotExist:
            raise PromocionError(u"La promoción asociada al código %s no existe."%kwargs['codigo'])
        except Exception, a_mensaje:
            raise Exception(a_mensaje)
        return self_

    def __init__(self, **kwargs):
        self.codigo = self._orm.codigo
        self.nombre = self._orm.nombre
        self.precio_costo = self._orm.precio_costo
        self.precio_venta = self._orm.precio_venta
        self.cantidad_productos = self._orm.cantidad_productos
        self.set_descripcion(kwargs['descripcion'])
        self._productos = self.set_elementos(kwargs['descripcion_productos'], kwargs.get('verificar_existencia'))
        self._categoria_orm = self._orm.categoria

    def set_elementos(self, a_descripcion, verificar_):
        productos_ = []
        verificar_ = False if verificar_ is None else True
        try:
            for producto_ in self._orm.productos.all():

                productos_.append(Elemento(producto_pk=producto_.id,promocion_pk=self._orm.id,descripcion=a_descripcion, verificar_existencia=verificar_))
        except ProductoExistenciaError, a_mensaje:
            raise PromocionExistenciaError(u'%s - %s'%(self.get_descripcion_excepcion(),a_mensaje))
        return productos_

    def get_elementos(self):
        return self._productos

    productos = property(get_elementos,set_elementos)

    def get_codigo_barra(self):
        return self.codigo

    def get_precio_unitario(self):
        return self.precio_venta

    def get_descripcion(self):
        return self.descripcion

    def set_descripcion(self, a_descripcion):
        descripcion_ = u""
        for campo_ in a_descripcion:
            if campo_ == 'precio_venta':
                descripcion_ += " " + u"%s"%formato_dinero(self.__dict__[campo_])
            else:
                descripcion_ += " " + u"%s"%self.__dict__[campo_]
        self.descripcion = descripcion_

    def get_descripcion_excepcion(self):
        return u"%s %s"%(self.descripcion, formato_dinero(self.precio_venta))

    def get_exento_iva(self):
        return False

    def verificar_existencia_requerida(self, a_cantidad_requerida):
        """
            Implementación de método abstracto para verificar que todas las
            existencias que componen a la promocion cumplan con la cantidad
            de existencia necesarias.  Es importante señalar que también
            se verifican los productos compuestos que componen a una
            promoción. p.e.: six pack de cerveza
        """
        for elemento_ in self._productos:
            if elemento_.producto.producto_compuesto():
                self.verificar_existencia_requerida_compuesto(a_cantidad_requerida,elemento_)
            else:
                try:
                    self.disponibilidad(elemento_.producto.stock_actual,
                                        a_cantidad_requerida,
                                        elemento_.cantidad)
                except DetalleError as detalle_error_:
                    mensaje_ = "%s - %s"%(elemento_.existencia.get_descripcion(),detalle_error_)
                    raise DetalleError(mensaje_)

    def verificar_existencia_requerida_compuesto(self, a_cantidad_requerida, a_elemento):
        producto_ = a_elemento.producto
        for componente_ in producto_.componentes:
            multiplicador_ = componente_.cantidad_compone * a_elemento.cantidad
            try:
                self.disponibilidad(componente_.stock_actual,a_cantidad_requerida,multiplicador_)
            except DetalleError as detalle_error_:
                mensaje_ = "%s - %s"%(componente_.get_descripcion(),detalle_error_)
                raise DetalleError(mensaje_)

    def disponibilidad(self, a_cantidad_existencia, a_cantidad_requerida, a_multiplicador=1):
        """
            Método que calcula la diferencia que existe entre la cantidad de existencia real
            y la cantidad de existencia que se requiere, si no hay existencias suficientes
            se levanta una excepcion indicando esta situación.
        """
        if a_cantidad_existencia - (a_cantidad_requerida * a_multiplicador) < 0:
            raise PromocionError(u"No hay existencias suficientes, solamente hay disponibles %s"%(a_cantidad_existencia/a_multiplicador))

    def get_orm(self):
        return self._orm

    def get_id(self):
        return self._orm.id

    def save_elementos(self, a_linea_detalle, a_bodega):
        """
            Método utilizado para poder descontar las existencias de la base de datos
        """
        for elemento_ in self.__elemento:
            post_save_linea_detalle_promocion.send(
                                               sender=elemento_,
                                               bodega=a_bodega,
                                               linea_detalle=a_linea_detalle)

    def descontar_stock_actual(self, a_cantidad):
        """
            Método utilizado para poder descontar las existencias de la base de datos
        """
        for elemento_ in self._productos:
            elemento_.producto.descontar_stock_actual(elemento_.cantidad * a_cantidad)

    def aumentar_stock_actual(self, cantidad_):
        """
            Método utilizado para poder aumentar las existencias de la base de datos
        """
        for elemento_ in self._productos:
            elemento_.producto.aumentar_stock_actual(elemento_.cantidad * cantidad_)

    def get_cantidad_disponible_devolucion(self, turno_):
        """
            Método que retorna la cantidad de existencias que se han
            vendido con el turno indicado.
        """
        try:
            cantidad_vendida = models.LineaDetalle.objects.filter(
                                          promocion__pk=self.get_id(),
                                          venta__turno__pk=turno_.get_id()
                                          ).aggregate(cantidad=Sum('cantidad'))['cantidad']

            cantidad_devuelta = devolucion_models.Devolucion.objects.filter(
                                        promocion__pk=self.get_id(),
                                        turno__pk=turno_.get_id()
                                                ).aggregate(cantidad=Sum('cantidad_productos'))['cantidad']
        except:
            return ExistenciaError(u"Sucedió un problema calculando la cantidad vendida de la existencia.")
        else:
            cantidad_vendida = 0 if cantidad_vendida is None else cantidad_vendida
            cantidad_devuelta = 0 if cantidad_devuelta is None else cantidad_devuelta
            return cantidad_vendida - cantidad_devuelta


class Elemento(object):

    def __new__(cls, **kwargs):
        self_ = super(Elemento,cls).__new__(cls)
        self_._orm = None
        if len(kwargs) == 0:
            return self_
        try:
            self_._orm = mantenedor_models.ProductoPromocion.objects.get(
                producto__pk=kwargs['producto_pk'],
                promocion__pk=kwargs['promocion_pk'])
        except models.ProductoPromocion.DoesNotExist:
            raise ElementoError(u"El elemento asociada a este código %s no existe"%kwargs['codigo_barra'])
        return self_

    def __init__(self, **kwargs):
        self._producto = Producto(verificar_existencia=kwargs['verificar_existencia'],codigo_barra=self._orm.producto.codigo_barra, descripcion=kwargs['descripcion'])
        self.cantidad = self._orm.cantidad

    def get_descripcion(self):
        return u"" + unicode(self.cantidad) + ' ' + self._producto.get_descripcion()

    def get_producto(self):
        return self._producto

    producto = property(get_producto)
