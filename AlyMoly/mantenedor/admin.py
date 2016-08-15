#-*- encoding: UTF-8 -*-
from AlyMoly.mantenedor.models import Producto, Bodega, Categoria, Promocion, ProductoPromocion, Proveedor, Trabajador
from AlyMoly.mantenedor.forms import BodegaForm, CategoriaForm, ProductoForm, PromocionForm, ProveedorForm, TrabajadorForm
from django.contrib import admin
from django.contrib.auth.models import User
from AlyMoly.mantenedor import recursos


class ProductoAdmin(admin.ModelAdmin):
    form = ProductoForm
    search_fields = ['=codigo_barra','nombre']
    list_display = ('codigo_barra','nombre','marca','categoria','tipo_envase','capacidad','precio_venta')
    list_editable = ('precio_venta',)
    list_filter = ('codigo_manual','exento_iva','es_compuesto')
    fieldsets = (
        ('Producto', {'classes': ['extrapretty'],
         'description':'En el siguiente formulario se registran los datos de un nuevo \
         <strong>Producto</strong>. <br /><br /> ',
            'fields' : (('categoria','subcategoria'),('codigo_barra', 'codigo_manual','exento_iva', 'es_compuesto')
                        ,('nombre','marca'),('tipo_envase','capacidad'),('precio_costo',
                        'precio_venta',),'stock_critico')
            }),
        ('Composición', {'classes': ['extrapretty'],
            'fields' : ( ('compuesto_por',
                        'cantidad_compuesto',), )
            }),

    )


class BodegaAdmin(admin.ModelAdmin):
    form = BodegaForm
    list_display = ('ubicacion','venta')
    fieldsets = (
        ('Bodega', {'classes': ['extrapretty'],
         'description':"En el siguiente formulario se registran los datos de una nueva \
         <strong>Bodega</strong>. <br/><br/>Una Bodega es el lugar físico en donde se \
         guardan las existencias de los productos, por lo anterior es necesario conocer\
          su <strong>ubicación</strong>, y su <strong>tipo</strong>.<br/><br/>",
            'fields' : ('ubicacion','venta','descripcion'
                        )
            }),
    )

class CategoriaAdmin(admin.ModelAdmin):
    form = CategoriaForm
    search_fields = ['nombre']
    fieldsets = (
        ('Categoría', {'classes': ['extrapretty'],
         'description':'En el siguiente formulario se registran los datos de una nueva \
         <strong>Categoría</strong>. <br /><br />Una categoría agrupa uno o más productos. Es \
         importante que los productos sean asignados a la categoría o subcategoría \
         correspondiente, para que los reportes (informes) del sistema sean óptimos al \
         momento de entregar la información. El campo <strong>Categoría Superior</strong> \
         es opcional, y se utiliza para asociar la categoría actual a una categoría superior,\
          en otras palabras, la categoría actual sería una subcategoría. Por ejemplo: se crea \
          la categoría de nombre <i>Gran Reserva</i> y asociarlo a una categoría \
          superior llamada <i>Vino</i>, entonces la categoría <i>Gran Reserva</i> sería una \
          subcategoría de <i>Vino</i>.<br/><br/>',
            'fields' : ('nombre','supercategoria'
                        )
            }),
    )
    def get_form(self, request, obj=None, **kwargs):
        form = super(CategoriaAdmin,self).get_form(request, obj,**kwargs)
        # Filtro las categorías que no son categorias superiores, es decir,
        # las categorias que ya tienen una supercategoria definida
        form.base_fields['supercategoria'].queryset = \
                        form.base_fields['supercategoria'].queryset.filter(supercategoria=None)
        return form
    list_display = ('nombre','categoria_superior')

class ProductoPromocionInline(admin.TabularInline):
    raw_id_fields = ("producto",)
    list_display = ('cantidad',)
    model = ProductoPromocion
    extra = 1

class PromocionAdmin(admin.ModelAdmin):
    form = PromocionForm
    search_fields = ['codigo','nombre']
    inlines = (ProductoPromocionInline,)
    list_display = ('codigo','nombre','categoria','precio_venta')
    list_editable = ('precio_venta',)
    fieldsets = (
        ('Promoción', {'classes': ['extrapretty'],
         'description':"""En el siguiente formulario se registran los datos de una nueva
         <strong>Promoción</strong>. <br /><br /> Una promoción agrupa varios productos existentes,
          y define un precio especial.<br/><br/>""",
            'fields' : ('codigo','nombre','categoria','precio_costo','precio_venta'
                        )
            }),
    )

class ProveedorAdmin(admin.ModelAdmin):
    form = ProveedorForm
    fieldsets = (
        ('Proveedor', {'classes': ['extrapretty'],
         'description':"""En el siguiente formulario se registran los datos de un nuevo
         <strong>Proveedor</strong>. <br /><br /> Un proveedor es quien distribuye los
         productos a la botillería, y los ingresos de bodega se hacen al proveedor correspondiente.<br/><br/>""",
            'fields' : ('rut','direccion','razon_social','fono','contacto'
                        )
            }),
    )


class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ('nombre','apellido_paterno','apellido_materno','es_activo')
    actions= ['activar','desactivar']
    form = TrabajadorForm
    fieldsets = (
        ('Trabajador', {'classes': ['extrapretty'],
         'description':"""En el siguiente formulario se registran los datos de un nuevo <strong>Vendedor</strong>.
                    <br/>
                    <br/>
                    Un vendedor es quien registra las ventas en el terminal de punto de venta. Por facilidad de uso la contrase&ntilde;a del vendedor ser&aacute; su n&uacute;mero de c&eacute;dula de identidad.
                    <br/>
                    <br/>""",
            'fields' : ('cedula_identidad','nombre','apellido_paterno','apellido_materno','estado'
                        )
            }),
    )

    def activar(self, request, queryset):
        users = User.objects.filter(pk__in=queryset.values_list('user__id',flat=True))
        rows_updated = users.update(is_active=True)
        if rows_updated == 1:
            message_bit = "1 trabajador fue"
            plural_bit = ""
        else:
            message_bit = "%s trabajadores fueron" % rows_updated
            plural_bit = "s"
        self.message_user(request, "%s satisfactoriamente activado%s" % (message_bit,plural_bit))
    activar.short_description = "Activa a los trabajadores seleccionados"

    def desactivar(self, request, queryset):
        users = User.objects.filter(pk__in=queryset.values_list('user__id',flat=True))
        rows_updated = users.update(is_active=False)
        if rows_updated == 1:
            message_bit = "1 trabajador fue"
            plural_bit = ""
        else:
            message_bit = "%s trabajadores fueron" % rows_updated
            plural_bit = "s"
        self.message_user(request, "%s satisfactoriamente desactivado%s" % (message_bit,plural_bit))

    desactivar.short_description = "Desactiva a los trabajadores seleccionados"

    def get_actions(self, request):
        actions = super(TrabajadorAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        """Este modelo no tiene permisos de eliminar para ningún rol"""
        return False

    def save_model(self, request, trabajador_, form, change):
        user_ = None
        if not change:
            ci_ = unicode(trabajador_.cedula_identidad) + recursos.calcular_dv(trabajador_.cedula_identidad)
            user_ = User.objects.create_user(username=ci_,password=ci_,email='')
            trabajador_.user_id = user_.id
        else:
            user_ = trabajador_.user
        user_.is_active = form.cleaned_data.get('estado')
        user_.save()
        trabajador_.save()




admin.site.register(Producto,ProductoAdmin)
admin.site.register(Bodega,BodegaAdmin)
admin.site.register(Categoria,CategoriaAdmin)
admin.site.register(Promocion,PromocionAdmin)
admin.site.register(Proveedor,ProveedorAdmin)
admin.site.register(Trabajador,TrabajadorAdmin)
