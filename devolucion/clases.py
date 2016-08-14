#!/usr/bin/env python
#-*- encoding: UTF-8 -*-

###############################################
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# �Milton Inostroza Aguilera                  #
# minostro@crecelibre.cl                      #
# 2009                                        #
###############################################

from django.db import transaction
from venta import clases as venta_clases
from devolucion import models
from devolucion import excepciones


class Devolucion(object):

    def __new__(cls, *args, **kwargs):
        self_ = object.__new__(cls)
        self_._orm = None       
        if len(kwargs) == 0:
            return self_
        #buscar venta en bd
        return self_

    def __init__(self, **kwargs):
        self.fecha_devolucion = kwargs['fecha_devolucion']
        self._monto_total = 0
        self.monto_unidad = 0
        self.cantidad_productos = 0
        self._turno = kwargs['turno']
        self._linea_detalle = None

    def add_linea_detalle(self, linea_detalle_):
        self._linea_detalle = linea_detalle_
        self.calcular_totales(self._linea_detalle)
        return self._linea_detalle

    def get_linea_detalle(self):
        return self._linea_detalle
    
    linea_detalle = property(get_linea_detalle, add_linea_detalle)
    
    def get_turno(self):
        return self._turno
    
    turno = property(get_turno)

    def verificar_operacion(self):
        if self._linea_detalle is None:
            raise Exception(u"Debe devolver al menos un Producto o Promoción.")
        if not self.turno.activo():
            raise VentaError(u"Turno en estado cerrado, favor inicie nuevamente sesión.")

    def calcular_totales(self, linea_detalle_):
        self.cantidad_productos = linea_detalle_.cantidad 
        self._monto_total = linea_detalle_.get_precio_total()

    def delete_linea_detalle(self, a_codigo):
        try:
            self._linea_detalle = None
            self.cantidad_productos = 0
            self._monto_total = 0
        except KeyError:
            pass
    
    def aumentar_linea_detalle(self, a_codigo):     
        try:
            linea_detalle_ = self._linea_detalle
            linea_detalle_.cantidad += 1
            self.calcular_totales(linea_detalle_)
            return linea_detalle_
        except Exception, a_mensaje:
            raise excepciones.DevolucionError(a_mensaje)
    
    def disminuir_linea_detalle(self, a_codigo):      
        try:
            linea_detalle_ = self._linea_detalle
            linea_detalle_.cantidad -= 1
            self.calcular_totales(linea_detalle_)
            return linea_detalle_
        except Exception, a_mensaje:
            raise excepciones.DevolucionError(a_mensaje)

    @transaction.commit_manually
    def save(self):
        self.verificar_operacion()
        self._orm = models.Devolucion()
        self._orm.__dict__.update({
             'monto_total': self._monto_total,
             'fecha_devolucion': self.fecha_devolucion,
             'cantidad_productos': self.cantidad_productos,
             'monto_unidad': self.linea_detalle.get_precio_unitario(),
             'turno_id': self._turno.id
         })
        monto_exento = 0
        monto_afecto = 0
        elemento = self._linea_detalle.get_especificacion()
        if self._linea_detalle.get_tipo().__name__ == venta_clases.Promocion.__name__:
            self._orm.__dict__.update({'promocion_id':elemento.get_id()})
            monto_afecto = self._monto_total
        elif self._linea_detalle.get_tipo().__name__ == venta_clases.Producto.__name__:
            self._orm.__dict__.update({'producto_id':elemento.orm.producto.id})
            if elemento.exento_iva:
                monto_exento = self._monto_total
            else:
                monto_afecto = self._monto_total
        try:
            self._orm.save()
            elemento.aumentar_stock_actual(self.cantidad_productos)
            self._turno.disminuir_totales(self._monto_total,monto_afecto,monto_exento)
            transaction.commit()
        except Exception, a_mensaje:
            transaction.rollback()
            raise excepciones.DevolucionError(a_mensaje)


class LineaDetalle(object):
    
    def __init__(self, devolucion_, a_especificacion, a_cantidad):
        self.devolucion = devolucion_
        self._especificacion_linea = a_especificacion
        self.cantidad = int(a_cantidad)
    
    def get_cantidad(self):
        return self._cantidad
    
    def set_cantidad(self, a_cantidad):
        """
            Cada modificación que se realice en la cantidad requerida en la
            linea de detalle es auditada para verificar disponibilidad de
            la especificacion.
        """
        self._cantidad = a_cantidad
        self.existencia_suficiente(self.devolucion.turno,a_cantidad)
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
    
    def existencia_suficiente(self, turno_, cantidad_):
        cantidad_disponible = self._especificacion_linea.get_cantidad_disponible_devolucion(turno_)
        if cantidad_ > cantidad_disponible:
            raise excepciones.DevolucionError(u"Sólo tiene %s %s para devolver"%(cantidad_disponible, self.get_descripcion()))            
    
    def get_tipo(self):
        return self._especificacion_linea.__class__


