#-*- encoding: UTF-8 -*-
###############################################
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@crecelibre.cl                      #
# ©Andrés Otárola Alvarado                    #
# aotarola@crecelibre.cl                      #
# 2010                                        #
###############################################

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, post_delete
from django.utils.safestring import mark_safe
from AlyMoly.mantenedor.signals import normalizar_campos
from AlyMoly.mantenedor.signals import contar_productos
from AlyMoly.mantenedor.signals import calcular_dv
from AlyMoly.mantenedor.signals import calcular_dv_trabajador
from AlyMoly.mantenedor.signals import iniciar_nuevo_inventario
from AlyMoly.mantenedor.signals import nuevo_producto_inventario

class Categoria(models.Model):
    """Representa una categoria a la que pertenece un producto"""
    nombre = models.CharField(
        max_length=200, unique=True, help_text=u'escriba el nombre de la categoría.')
    supercategoria = models.ForeignKey(
        'self', verbose_name=u"Categoría Superior", null=True, blank=True)

    def categoria_superior(self):
        if self.supercategoria:
            return mark_safe(u"""%s""" % self.supercategoria.nombre)
        else:
            return mark_safe(u"")
    categoria_superior.allow_tags = True
    categoria_superior.short_description = u'categoría superior'
    categoria_superior.admin_order_field = 'nombre'

    def __unicode__(self):
        return self.nombre.capitalize()

    class Meta:
        verbose_name = u"categoría"
        verbose_name_plural = u"categorías"
        ordering = ['nombre']


class Producto(models.Model):
    codigo_barra = models.CharField(
        max_length=100, unique=True, verbose_name=u"código de barra")
    codigo_manual = models.BooleanField(verbose_name=u"código manual")
    nombre = models.CharField(
        max_length=200, help_text='Escriba el nombre del producto.')
    marca = models.CharField(
        max_length=50, help_text='Escriba la marca del producto.')
    tipo_envase = models.CharField(max_length=50, null=True, blank=True, verbose_name=u'tipo de envase',
                                   help_text='Escriba el tipo de envase del producto, \
                                       <br />por ejemplo lata, botella, bolsa, etc.')
    capacidad = models.CharField(max_length=50, null=True, blank=True,
                                 help_text='ingrese capacidad del producto, por ejemplo 350cc ó 120gr')
    precio_costo = models.PositiveIntegerField(verbose_name=u'precio de costo',
                                               help_text=u'Ingrese el precio de costo del producto.&nbsp;&nbsp;\
                                       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
    precio_venta = models.PositiveIntegerField(verbose_name=u'precio de venta',
                                               help_text=u'Ingrese el precio de venta del producto.')
    exento_iva = models.BooleanField(verbose_name=u'exento I.V.A')
    cantidad_compone = models.IntegerField(default=0, verbose_name=u'cantidad que compone',
                                           help_text='Si el producto compone a otro producto, <br />debe\
                                            indicar la cantidad que va a componer &nbsp;<br />dicho \
                                           producto, por ejemplo 6 latas de <br />cervezas componen un display.')
    compone = models.ForeignKey('self', verbose_name=u'compone a producto', null=True, blank=True,
                                help_text='Si el producto compone a otro producto, debe <br />ingresar \
                                el código de barra de ese producto,<br /> por  ejemplo si esta creando \
                                una lata de <br />cerveza, entonces debe ingresar el código de<br /> barra \
                                del display que compone.')
    subcategoria = models.ForeignKey('Categoria', verbose_name=u"Sub-Categoría",
                                     help_text=u'Seleccione la subcategoría a la cual pertenece el producto')
    stock_critico = models.PositiveIntegerField(verbose_name=u"Stock crítico")

    es_compuesto = models.BooleanField(verbose_name=u'compuesto')

    def categoria(self):
        nombre = self.subcategoria.nombre
        if self.subcategoria.supercategoria:
            nombre = self.subcategoria.supercategoria.nombre + ' / ' + nombre
        return mark_safe(u"""%s""" % nombre)
    categoria.allow_tags = True
    categoria.short_description = u'categoría'
    categoria.admin_order_field = 'subcategoria'

    def __unicode__(self):
        return "%s %s %s" % (self.nombre.capitalize(), self.tipo_envase, self.capacidad)

    def save(self, force_insert=False, force_update=False):
        super(Producto, self).save(force_insert, force_update)
        if self.es_compuesto:
            p = Producto.objects.get(codigo_barra=getattr(self,'_compuesto_por'))
            p.compone = self
            p.cantidad_compone = getattr(self,'_cantidad_compone')
            p.save()

    class Meta:
        ordering = ['nombre']


class Bodega(models.Model):
    """Representa a la bodega que contiene productos"""
    ubicacion = models.CharField(max_length=200, unique=True, verbose_name=u"ubicación",
                                 help_text=u'Describa la ubicación física de la bodega.')
    descripcion = models.TextField(null=True, blank=True, verbose_name=u"descripción",
                                   help_text=u'Escriba una descripción para conocer el propósito de la bodega.')
    venta = models.BooleanField(default=False, help_text=u'Indique si esta bodega corresponde a una \
                                                            bodega de venta.')
    productos = models.ManyToManyField(
        'Producto', through='movimiento.ProductoBodega')

    def __unicode__(self):
        return self.ubicacion.capitalize()

    def save(self, force_insert=False, force_update=False):
        """
            Al guardar una bodega se restringe que exista una única bodega del tipo
            venta para la sucursal.
        """
        if self.venta and len(Bodega.objects.exclude(id=self.id).filter(venta=True)) > 0:
            raise Exception("Usted ya cuenta con una bodega de venta")
        super(Bodega, self).save(force_insert, force_update)


class Promocion(models.Model):
    codigo = models.CharField(
        max_length=100, unique=True, verbose_name=u"código promoción")
    nombre = models.CharField(max_length=255, unique=True)
    precio_costo = models.PositiveIntegerField(verbose_name=u"precio de costo")
    precio_venta = models.PositiveIntegerField(verbose_name=u"precio de venta")
    cantidad_productos = models.IntegerField(null=True, blank=True)
    productos = models.ManyToManyField(Producto, through='ProductoPromocion')
    categoria = models.ForeignKey('Categoria', verbose_name=u"Categoría",
                                  help_text=u'Seleccione la categoría a la cual pertenece la promoción')

    def codigo_barra(self):
        return self.codigo

    def __unicode__(self):
        return u'%s' % (self.nombre)

    class Meta:
        verbose_name = u"promoción"
        verbose_name_plural = u"promociones"


class ProductoPromocion(models.Model):
    producto = models.ForeignKey('Producto')
    promocion = models.ForeignKey('Promocion')
    cantidad = models.PositiveIntegerField()

    def __unicode__(self):
        return u' '

    class Meta:
        verbose_name_plural = u"productos de promoción"
        unique_together = ('producto', 'promocion')


class Proveedor(models.Model):
    rut = models.PositiveIntegerField(u"R.U.T.", unique=True)
    dv = models.CharField(max_length=1, null=False, blank=False)
    direccion = models.CharField(max_length=200, verbose_name=u"dirección",
                                 help_text=u"Ingrese nombre de calle y número.")
    razon_social = models.CharField(max_length=100, unique=True, verbose_name=u"Razón social",
                                    help_text=u"Ingrese la razón social.")
    fono = models.CharField(max_length=200, verbose_name=u"Teléfono",
                            help_text=u"Teléfono de contacto.")
    contacto = models.CharField(max_length=200, null=True, blank=True, verbose_name=u"Nombre de contacto",
                                help_text=u"Ingrese el nombre de la persona de contacto del proveedor.")
    ingresos = models.ManyToManyField(
        'movimiento.ProductoBodega', through='movimiento.Ingreso')

    def __unicode__(self):
        return u'%s' % (self.razon_social.capitalize())

    class Meta:
        verbose_name = u"proveedor"
        verbose_name_plural = u"proveedores"


class Trabajador(models.Model):
    cedula_identidad = models.PositiveIntegerField(
        u"Cédula de identidad", unique=True)
    digito_verificador = models.CharField(max_length=1, null=False, blank=True)
    nombre = models.CharField(max_length=150)
    apellido_paterno = models.CharField(max_length=150)
    apellido_materno = models.CharField(max_length=150)
    user = models.OneToOneField(
        User, verbose_name=u'Usuario', null=True, blank=True)

    def es_activo(self):
        return self.user.is_active
    es_activo.boolean = True
    es_activo.short_description = u'Activo'

    def __unicode__(self):
        return u'%s' % (self.nombre_completo())

    def nombre_completo(self):
        return "%s %s %s" % (' '.join(nombre_.capitalize() for nombre_ in self.nombre.split(' ')),
                             self.apellido_paterno.capitalize(),
                             self.apellido_materno.capitalize())
    nombre_completo.short_description = u'nombre completo'

    def get_cedula_identidad(self):
        return str(self.cedula_identidad) + "-" + str(self.digito_verificador)

    get_cedula_identidad.short_description = u'cédula de identidad'

    class Meta:
        verbose_name = u"trabajador"
        verbose_name_plural = u"trabajadores"


# pre
pre_save.connect(normalizar_campos, Bodega)
pre_save.connect(normalizar_campos, Categoria)
pre_save.connect(normalizar_campos, Producto)
pre_save.connect(normalizar_campos, Promocion)
pre_save.connect(normalizar_campos, Proveedor)
pre_save.connect(normalizar_campos, Trabajador)
pre_save.connect(calcular_dv, Proveedor)
pre_save.connect(calcular_dv_trabajador, Trabajador)

# post
post_save.connect(contar_productos, ProductoPromocion)
post_delete.connect(contar_productos, ProductoPromocion)
post_save.connect(iniciar_nuevo_inventario, Bodega)
post_save.connect(nuevo_producto_inventario, Producto)
