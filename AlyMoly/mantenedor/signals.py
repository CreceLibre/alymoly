#-*- encoding: UTF-8 -*-
from django.apps import apps
from django.db import transaction

def normalizar_campos(sender,**kwargs):
    "Normaliza campos de modelos con minúsculas cerradas"
    instancia = kwargs['instance']
    for theField in instancia._meta.local_fields:
        if theField.rel == None and not theField.primary_key:
            try:
                instancia.__dict__.update({theField.name:instancia.__dict__[theField.name].lower().strip()})
            except AttributeError:
                pass

def contar_productos(sender,**kwargs):
    """Cuenta la cantidad de productos de una promoción y
    asigna el valor calculado a la promoción"""
    promocion = kwargs['instance'].promocion
    cantidad = 0
    for producto in promocion.productopromocion_set.all():
        cantidad = cantidad + producto.cantidad
    promocion.cantidad_productos = cantidad
    promocion.save()

def calcular_dv(sender,**kwargs):
    """calcula el dv de un rut chileno"""
    obj = kwargs['instance']
    rut = unicode(obj.rut)
    suma  = 0
    multi = 2
    for r in rut[::-1]:
        suma  += int(r) * multi
        multi += 1
        if multi == 8:
            multi = 2
    obj.dv = u'0123456789K0'[11 - suma % 11]
    obj.save

def calcular_dv_trabajador(sender,**kwargs):
    """calcula el dv de una cedula de identidad chilena"""
    obj = kwargs['instance']
    rut = unicode(obj.cedula_identidad)
    suma  = 0
    multi = 2
    for r in rut[::-1]:
        suma  += int(r) * multi
        multi += 1
        if multi == 8:
            multi = 2
    obj.digito_verificador = u'0123456789K0'[11 - suma % 11]
    obj.save

@transaction.atomic
def iniciar_nuevo_inventario(sender,**kwargs):
    """Realiza un inventario con stock 0 para una nueva Bodega"""
    bodega = kwargs['instance']
    if bodega.productos.count() == 0:
        ProductoBodega = apps.get_model('movimiento','ProductoBodega')
        Producto = apps.get_model('mantenedor','Producto')
        productos = Producto.objects.all()
        for producto in productos:
            existencia = ProductoBodega(producto=producto,bodega=bodega, existencia=0)
            existencia.save()

@transaction.atomic
def nuevo_producto_inventario(sender,**kwargs):
    """cuando se agrega un producto nuevo, se verifica si existe
     en los inventarios existentes, si no exite, se crea."""
    producto = kwargs['instance']
    Bodega = apps.get_model('mantenedor','Bodega')
    ProductoBodega = apps.get_model('movimiento','ProductoBodega')
    for bodega in Bodega.objects.all():
        if not bodega.productos.all().filter(id=producto.id):
            existencia = ProductoBodega(producto=producto,bodega=bodega, existencia=0)
            existencia.save()
