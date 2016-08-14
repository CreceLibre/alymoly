#!/usr/bin/env python
#-*- encoding: UTF-8 -*-

###############################################
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# Milton Inostroza Aguilera                   #
# minostro@crecelibre.cl                      #
# 2009                                        #
###############################################
from django.db.models.loading import get_model 
from django.dispatch import Signal

post_save_linea_detalle_existencia = Signal(providing_args=["bodega"])
post_save_devolucion = Signal(providing_args=["bodega"])
post_save_linea_detalle_promocion = Signal(providing_args=["bodega","linea_detalle"])
post_save_linea_detalle_existencia_compuesta = Signal(providing_args=["bodega","linea_detalle"])
post_save_devolucion_compuesta = Signal(providing_args=["bodega","devolucion"])

def descontar_existencia_producto(**kwargs):
    """
        se descuenta la cantidad correspondiente a cada item
        de la venta siempre y cuando este item sea un producto.
    """
    linea_detalle_ = kwargs['sender']
    if linea_detalle_.producto is None:
        return
    bodega_ = kwargs['bodega'].get_bodega_orm()
    existencia_ = get_model('movimiento','ProductoBodega').objects.get(bodega=bodega_,producto=linea_detalle_.producto)
    existencia_.existencia -= linea_detalle_.cantidad
    existencia_.save()

def descontar_existencia_producto_compuesto(**kwargs):
    """
        se descuenta la cantidad correspondiente a cada item
        de la venta siempre y cuando este item sea un producto compuesto.
    """
    elemento_ = kwargs['sender']
    bodega_ = kwargs['bodega'].get_bodega_orm()
    linea_detalle_ = kwargs['linea_detalle']
    producto_ = elemento_.get_existencia_orm().producto
    existencia_ = get_model('movimiento','ProductoBodega').objects.get(bodega=bodega_,producto=producto_)
    existencia_.existencia -= producto_.cantidad_compone * linea_detalle_.cantidad
    existencia_.save()
    
    
def descontar_existencia_promocion(**kwargs):
    """
        se descuenta la cantidad correspondiente a cada item
        de la venta siempre y cuando este item sea una promocion.
    """
    elemento_ = kwargs['sender']
    bodega_ = kwargs['bodega'].get_bodega_orm()
    linea_detalle_ = kwargs['linea_detalle']
    producto_ = elemento_.get_elemento_orm().producto
    existencia_ = get_model('movimiento','ProductoBodega').objects.get(bodega=bodega_,producto=producto_)
    existencia_.existencia -= elemento_.cantidad * linea_detalle_.cantidad 
    existencia_.save()

def aumentar_existencia_producto(**kwargs):
    """
        se aumenta la cantidad correspondiente a cada item
        de la devolucion siempre y cuando este item sea un producto.
    """
    devolucion_ = kwargs['sender']
    if devolucion_.producto is None:
        return
    bodega_ = kwargs['bodega'].get_bodega_orm()
    existencia_ = get_model('movimiento','ProductoBodega').objects.get(bodega=bodega_,producto=devolucion_.producto)
    existencia_.existencia += devolucion_.cantidad_productos
    existencia_.save()

def aumentar_existencia_producto_compuesto(**kwargs):
    """
        se aumenta la cantidad correspondiente a cada item
        de la devolucion siempre y cuando este item sea un producto compuesto.
    """
    elemento_ = kwargs['sender']
    bodega_ = kwargs['bodega'].get_bodega_orm()
    devolucion_ = kwargs['devolucion']
    producto_ = elemento_.get_existencia_orm().producto
    movimiento_ = get_model('movimiento','ProductoBodega').objects.get(bodega=bodega_,producto=producto_)
    movimiento_.existencia += producto_.cantidad_compone * devolucion_.cantidad_productos
    movimiento_.save()
    
post_save_linea_detalle_existencia.connect(descontar_existencia_producto)
post_save_linea_detalle_existencia_compuesta.connect(descontar_existencia_producto_compuesto)
post_save_linea_detalle_promocion.connect(descontar_existencia_promocion)
post_save_devolucion.connect(aumentar_existencia_producto)
post_save_devolucion_compuesta.connect(aumentar_existencia_producto_compuesto)