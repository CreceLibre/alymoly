#-*- encoding: UTF-8 -*-
from django import forms
from mantenedor.models import Bodega
from movimiento.models import ProductoBodega
from django.utils.safestring import mark_safe

class JQueryBaseForm(forms.Form):
    'Formulario base que añade los script de jquery'
    
    class Media:
        js = ('/media/static/js/jquery.js',
              '/media/static/js/jquery.capitalize.min.js',
              '/media/static/js/jquery.blockUI.js',
              '/media/static/js/jquery.alphanumeric.pack.js',
              '/media/static/js/jquery-ui-highlight.min.js',
              )

class BodegaBaseForm(JQueryBaseForm):
    'Formulario base que representa la selección sucursal/bodega'
    bodega = forms.ModelChoiceField(
                               required=True,
                               label=u"Bodega",
                               queryset=Bodega.objects.all(),
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               help_text=u"Seleccione la Bodega"
                               )

        
class BuscarExistenciaForm(JQueryBaseForm):
    texto = forms.CharField(widget=forms.TextInput(attrs={'class':'qs_input'}))
    
    def clean_texto(self):
        data = self.cleaned_data["texto"]
        return data.strip()
    
    class Media:
        js = (
              '/media/static/js/inventario/buscar/buscar.js',
              )

class StockCriticoForm(BodegaBaseForm):
    class Media:
        js = (
              '/media/static/js/inventario/critico/cargar.js',
              )

class InventarioActualForm(BodegaBaseForm):
    class Media:
        js = (
              '/media/static/js/inventario/actual/cargar.js',
              )
        
class ActualizarExistenciaForm(forms.Form):
    
    producto_bodega = forms.DecimalField(min_value=0)

    existencia = forms.DecimalField(min_value=0)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        producto_bodega = cleaned_data.get("producto_bodega")
        if producto_bodega:
            try:
                ProductoBodega.objects.get(pk=producto_bodega)
            except ProductoBodega.DoesNotExist: 
                del cleaned_data['producto_bodega']
                raise forms.ValidationError(u"No existe el producto de bodega seleccionado.")
        return cleaned_data
    
    
class ReiniciarInventarioForm(BodegaBaseForm):

    valor_reinicio = forms.IntegerField(label=u'Valor de reinicio',min_value=0,help_text=mark_safe(u'Valor único \
            por el cual el inventario sera <strong>reiniciado</strong>', ),
            widget=forms.TextInput(attrs={'style':'font-family:arial,sans-serif;font-size:17px;margin-bottom:0.2em'}))
    
    class Media:
        js = (
              '/media/static/js/inventario/actual/reiniciar.js',
              )