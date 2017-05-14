#-*- encoding: UTF-8 -*-
###############################################
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@minostro.com                       #
# 2009                                        #
###############################################
from django.db import models
from AlyMoly.mantenedor.models import Proveedor, Producto, Bodega
from django.db.models.signals import post_save, pre_save
from AlyMoly.movimiento.signal import ingreso_mercaderia, egreso_mercaderia, traspaso_mercaderia, actualizar_costo
from AlyMoly.tags.templatetags.tags import milesformat

class ProductoBodega(models.Model):
    """
    Representa las existencias de productos en una bodega
    """
    producto = models.ForeignKey(Producto)
    bodega = models.ForeignKey(Bodega)
    existencia = models.PositiveIntegerField()

    def __unicode__(self):
        return u'%s'%(self.producto.nombre + ' ' + self.bodega.ubicacion)

    def save(self, force_insert=False, force_update=False):
        """
            utilizado solamente para sqlite3, ya que no soporta unsigned integer.
            En la interfaz admin no hay problema ya que django provee verificación
            para el tipo de campo que es existencia, pero el problema está cuando
            se utiliza este campo en el proceso de venta.
        """
        if self.existencia < 0 and not len(ProductoBodega.objects.filter(producto=self.producto)) == 0:
            producto_bodega_ = ProductoBodega.objects.get(producto=self.producto,bodega=self.bodega)
            raise Exception(u"Para: %s existen solamente %s unidades"%(self.producto.nombre, producto_bodega_.existencia))
        super(ProductoBodega, self).save()

    class Meta:
        unique_together = ('producto','bodega')

class Traspaso(models.Model):
    """
    Representa los movimientos de traspaso entre bodegas
    """
    origen = models.ForeignKey(Bodega, related_name="origen", help_text=u'Seleccione la bodega de origen')
    destino = models.ForeignKey(Bodega, related_name="destino",help_text=u'Seleccione la bodega de destino')
    producto = models.ForeignKey(Producto)
    cantidad = models.PositiveIntegerField(help_text=u'Ingrese la cantidad de traspaso.')
    fecha_traspaso = models.DateField(
                               u'Fecha de Traspaso',
                               auto_now_add=True)

    def __unicode__(self):
        return u'Traspaso #%s' % self.id

    class Meta:
        verbose_name = u"Traspaso de mercadería"
        verbose_name_plural = u"Traspasos de mercaderías"

class Ingreso(models.Model):
    """
    Representa un ingreso de mercadería
    """
    existencia = models.ForeignKey(ProductoBodega)
    proveedor = models.ForeignKey(Proveedor, help_text=u"Seleccione el proveedor de ingreso de mercadería.")
    fecha_ingreso = models.DateField(
                               u'Fecha de Ingreso',
                               auto_now_add=True)
    cantidad = models.PositiveIntegerField(u"Stock de ingreso",
                                        help_text=u"Ingrese el stock \
                                        que se está recibiendo.")
    precio_costo = models.PositiveIntegerField(
                                   u"Precio costo de unidad ($), incluído I.V.A.",
                                   help_text=u"Ingrese el precio unitario de la mercadería.   ")

    def sucursal(self):
        return self.existencia.bodega.sucursal
    sucursal.short_description = u'sucursal'
    def bodega(self):
        return self.existencia.bodega.ubicacion
    bodega.short_description = u'bodega'
    def producto(self):
        return self.existencia.producto
    producto.short_description = u'producto'
    def costo(self):
        return milesformat(unicode(self.precio_costo))
    costo.short_description = u'costo CLP($)'
    def codigo_barra(self):
        return self.existencia.producto.codigo_barra
    codigo_barra.short_description = u'código de barra'

    def __unicode__(self):
        return u'%s' % self.existencia.producto.__unicode__()

    class Meta:
        verbose_name = u"Ingreso de mercadería"
        verbose_name_plural = u"Ingresos de mercaderías"

class Egreso(models.Model):
    """
    Representa un egreso de mercadería
    """
    existencia = models.ForeignKey(ProductoBodega)
    fecha_egreso = models.DateField(
                               u'Fecha de Egreso',
                               auto_now_add=True)
    cantidad = models.PositiveIntegerField(u"Cantidad de egreso",
                                        help_text=u"Ingrese la cantidad \
                                        que está egresando.")
    observacion = models.TextField(
                                   u"Obervación",
                                   help_text=u"Ingrese una observación de egreso.",
                                   null=True,blank=True)

    def sucursal(self):
        return self.existencia.bodega.sucursal
    sucursal.short_description = u'sucursal'
    def bodega(self):
        return self.existencia.bodega.ubicacion
    bodega.short_description = u'bodega'
    def producto(self):
        return self.existencia.producto
    producto.short_description = u'producto'
    def codigo_barra(self):
        return self.existencia.producto.codigo_barra
    codigo_barra.short_description = u'código de barra'

    def __unicode__(self):
        return u'%s' % self.existencia.producto.__unicode__()

    class Meta:
        verbose_name = u"Egreso de mercadería"
        verbose_name_plural = u"Egresos de mercaderías"

pre_save.connect(traspaso_mercaderia, Traspaso)
pre_save.connect(ingreso_mercaderia,Ingreso)
pre_save.connect(egreso_mercaderia,Egreso)
post_save.connect(actualizar_costo, Ingreso)
