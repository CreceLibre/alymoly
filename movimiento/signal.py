#-*- encoding: UTF-8 -*-
from django.db.models.loading import get_model 

def ingreso_mercaderia(sender,**kwargs):
    """Realiza el ingreso de mercadería. El proceso
    de aumentar existencias en inventario, sólo se realiza la primera
    vez que se crea el registro."""
    ingreso = kwargs['instance']
    if not ingreso.id:
        registro = ingreso.existencia
        bodega = ingreso.existencia.bodega
        producto_padre = ingreso.existencia.producto
        Producto = get_model('mantenedor','Producto')
        ProductoBodega = get_model('movimiento','ProductoBodega')
        producto_hijo = None
        cantidad = None
        try:#caso producto compuesto
            producto_hijo = Producto.objects.get(compone=producto_padre)
            cantidad = producto_hijo.cantidad_compone * ingreso.cantidad
            registro = ProductoBodega.objects.get(bodega=bodega,producto=producto_hijo)
        except Producto.DoesNotExist:
            cantidad = ingreso.cantidad 
        registro.existencia += cantidad
        registro.save()
        
def actualizar_costo(sender,**kwargs):
    """Realiza el roceso de actualización de costo de un producto al
    último costo ingresado."""
    ingreso = kwargs['instance']
    producto = ingreso.existencia.producto
    producto.precio_costo = ingreso.precio_costo
    producto.save()
    
def egreso_mercaderia(sender,**kwargs):
    """Realiza el egreso de mercadería. El proceso
    de disminuir existencias en inventario sólo se realiza la primera
    vez que se crea el registro."""
    egreso = kwargs['instance']
    if not egreso.id:
        registro = egreso.existencia
        bodega = egreso.existencia.bodega
        producto_padre = egreso.existencia.producto
        Producto = get_model('mantenedor','Producto')
        ProductoBodega = get_model('movimiento','ProductoBodega')
        producto_hijo = None
        cantidad = None
        try:#caso producto compuesto
            producto_hijo = Producto.objects.get(compone=producto_padre)
            cantidad = producto_hijo.cantidad_compone * egreso.cantidad
            registro = ProductoBodega.objects.get(bodega=bodega,producto=producto_hijo)
        except Producto.DoesNotExist:
            cantidad = egreso.cantidad 
        registro.existencia -= cantidad
        registro.save()
    
def traspaso_mercaderia(sender,**kwargs):
    """Realiza el traspaso de mercadería. El proceso
    de traspasar existencias en inventario entre bodegas, sólo se realiza la primera
    vez que se crea el registro."""
    traspaso = kwargs['instance']
    if not traspaso.id:
        producto_padre = traspaso.producto
        Producto = get_model('mantenedor','Producto')
        producto_hijo = None
        cantidad = None
        try:#caso producto compuesto
            producto_hijo = Producto.objects.get(compone=producto_padre)
            cantidad = producto_hijo.cantidad_compone * traspaso.cantidad
            producto = producto_hijo
        except Producto.DoesNotExist:
            cantidad = traspaso.cantidad
            producto = producto_padre

        ProductoBodega = get_model('movimiento','ProductoBodega')
        producto_origen = ProductoBodega.objects.get(
                                                       bodega=traspaso.origen, 
                                                       producto=producto)
        producto_destino = ProductoBodega.objects.get(
                                                        bodega=traspaso.destino, 
                                                        producto=producto)
        producto_origen.existencia -= cantidad
        producto_destino.existencia += cantidad
        producto_origen.save()
        producto_destino.save()
        