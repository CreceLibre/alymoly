#-*- encoding: UTF-8 -*-
from django.contrib import admin
from django import forms
from AlyMoly.movimiento.forms import IngresoMercaderiaForm, EgresoMercaderiaForm, TraspasoForm
from AlyMoly.movimiento.models import Ingreso, Egreso, Traspaso


class IngresoAdmin(admin.ModelAdmin):
    form = IngresoMercaderiaForm
    search_fields = ['existencia__producto__codigo_barra','existencia__producto__nombre', 'proveedor__razon_social']
    list_filter = ('proveedor',)
    list_display = ('id','proveedor','bodega','codigo_barra','producto','costo','cantidad','fecha_ingreso')
    fieldsets = (
        ('Ingreso de Mercadería', {'classes': ['extrapretty'],
         'description':'En el siguiente formulario se registran los movimientos de \
         <strong>Ingreso</strong> de existencias hacia una bodega. <br /><br /> ',
            'fields' : ('bodega',('existencia','cantidad'),('proveedor','precio_costo')
                        )
            }),
    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        # Se cambia el widget por defecto de la relación
        # FK recursiva, por un widdget de entrada de texto, de
        # el módulo Admin
        if db_field.attname == 'proveedor_id':
            kwargs['widget'] = forms.Select(attrs={'style':'width:230px'})
        return super(IngresoAdmin, self).formfield_for_dbfield(db_field, **kwargs)

class EgresoAdmin(admin.ModelAdmin):
    form = EgresoMercaderiaForm
    search_fields = ['existencia__producto__codigo_barra','existencia__producto__nombre']
    list_display = ('id','bodega','codigo_barra','producto','cantidad','fecha_egreso')
    fieldsets = (
        ('Egreso de Mercadería', {'classes': ['extrapretty'],
         'description':'En el siguiente formulario se registran los movimientos de \
         <strong>Egreso</strong> de existencias desde una bodega. <br /><br /> ',
            'fields' : ('bodega',('existencia','cantidad'),'observacion'
                        )
            }),
    )
class TraspasoAdmin(admin.ModelAdmin):
    form = TraspasoForm
    list_display = ('id','origen','destino','producto','cantidad','fecha_traspaso',)
    fieldsets = (
        ('Traspaso', {'classes': ['extrapretty'],
         'description':'En el siguiente formulario se registran el movimiento de un nuevo \
         <strong>Traspaso</strong> de existencias entre dos bodegas. <br /><br /> ',
            'fields' : (('origen','destino'),'producto', 'cantidad',
                        )
            }),
    )

admin.site.register(Ingreso,IngresoAdmin)
admin.site.register(Egreso,EgresoAdmin)
admin.site.register(Traspaso, TraspasoAdmin)
