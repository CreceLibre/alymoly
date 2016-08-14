#-*- encoding: UTF-8 -*-
from django import forms
from mantenedor.models import Proveedor, Categoria, Bodega
from reporte.clases import Reporte
from django.forms.util import ErrorList
import datetime

class ReporteForm(forms.Form):
    'Formulario que define el campo formato de un reporte'
    formato = forms.ChoiceField(
                               required=True,
                               label=u"Formato",
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               help_text=u"Seleccione el formato"
                               )
    def __init__(self, *args, **kwargs):
        super(ReporteForm, self).__init__(*args, **kwargs)        
        self.fields['formato'].choices = [(x,x.upper()) for x in Reporte.FORMATO]

class ExistenciaPorCategoriaForm(ReporteForm):
    'Formulario de generación de reporte de Existencia por categoría'
    
    bodega = forms.ModelChoiceField(
                               required=True,
                               label=u"Bodega",
                               queryset=Bodega.objects.all(),
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               help_text=u"Seleccione la Bodega"
                               )
    
    categoria = forms.ChoiceField(
                               required=True,
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               label=u"Categoría",
                               help_text=u"Seleccione la categoría",
                               )
    def __init__(self, *args, **kwargs):
        super(ExistenciaPorCategoriaForm, self).__init__(*args, **kwargs)
        self.fields['categoria'].choices = [('-1','TODAS')] + \
                                map(lambda x: (x.id,x.nombre.title()),
                                Categoria.objects.all())
                                
    def clean_bodega(self):
        bodega = self.cleaned_data["bodega"]
        return bodega.id

class TipoVentaForm(ReporteForm):
    'Formulario que define el tipo de venta: exenta, no exenta, todas'
    TODOS = 1
    EXENTOS = 2
    AFECTOS = 3
    OPCION_VENTA = (
                     (TODOS,'TODOS'),
                     (EXENTOS,'EXENTOS'),
                     (AFECTOS,'AFECTOS'),
                     )
    tipo = forms.ChoiceField(
                               required=True,
                               label=u"Tipo",
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               help_text=u"Seleccione el tipo de reporte de ventas",
                               choices = OPCION_VENTA
                               )
    
class ProductoForm(ReporteForm):
    'Formulario de generacion de reporte de Productos'
    TODOS = 1
    CODIGO_BARRA = 2
    CODIGO_MANUAL = 3
    EXENTOS = 4
    AFECTOS = 5
    PROMOCIONES = 6
    OPCION_PRODUCTO = (
                     (TODOS,'TODOS'),
                     (CODIGO_BARRA,'SOLO CODIGO DE BARRA'),
                     (CODIGO_MANUAL,'SOLO CODIGO MANUAL'),
                     (EXENTOS,'SOLO EXENTOS'),
                     (AFECTOS,'SOLO AFECTOS'),  
                     (PROMOCIONES,'SOLO PROMOCIONES'),                                                               
                     )
    
    tipo_producto = forms.ChoiceField(
                               required=True,
                               label=u"Tipo",
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               help_text=u"Seleccione el tipo de reporte de producto",
                               choices = OPCION_PRODUCTO
                               )

class VentasForm(TipoVentaForm):
    'Formulario de generaciñon de reporte de por rango de fecha'
    fecha_inicio = forms.DateField(input_formats = ['%d/%m/%Y'], 
                                   widget=forms.TextInput({'class':'tipo_fecha'}),
                                   help_text=u'Seleccione el período de inicio')
    fecha_fin = forms.DateField(label=u'Fecha término',input_formats = ['%d/%m/%Y'], 
                                   widget=forms.TextInput({'class':'tipo_fecha'}),
                                help_text=u'Seleccione el período de término')
    def __init__(self, *args, **kwargs):
        super(VentasForm, self).__init__(*args, **kwargs)
        self.fields['fecha_inicio'].initial = datetime.date.today().strftime('%d/%m/%Y')
        self.fields['fecha_fin'].initial = datetime.date.today().strftime('%d/%m/%Y')
        
    class Media:
        js = ('/media/static/js/jquery.js',
              '/media/static/js/jquery-ui-datepicker.min.js',
              '/media/static/js/reporte/ventas/seleccion_fecha.js',
              )
        css = {'all':('/media/static/css/datepicker/jquery-datepicker.css',)}
    
    def clean(self):
        """ Método de validación personalizado que válida si
        la fecha de inici sea menor que la fecha de término """
        cleaned_data = self.cleaned_data

        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")


        if fecha_inicio > fecha_fin:
            # Se ingresa la información de error.
            msg = u"La fecha de inicio debe ser menor que la fecha de término."
            self._errors["fecha_fin"] = ErrorList([msg])

            # Como estos campos ya no son válidos, entonces
            # se eliminan del diccionario de objetos válidos
            del cleaned_data["fecha_inicio"]
            del cleaned_data["fecha_fin"]

        # Se retorna el diccioario de datos limpios
        return cleaned_data
        
class VentasDiariasForm(TipoVentaForm):
    'Formulario de generación de reporte de ventas diarias'
    fecha = forms.DateField(input_formats = ['%d/%m/%Y'], 
                                   widget=forms.TextInput({'class':'tipo_fecha'}),
                                   help_text=u'Seleccione la fecha de venta')
    def __init__(self, *args, **kwargs):
        super(VentasDiariasForm, self).__init__(*args, **kwargs)
        self.fields['fecha'].initial = datetime.date.today().strftime('%d/%m/%Y')    
    
    class Media:
        js = ('/media/static/js/jquery.js',
              '/media/static/js/jquery-ui-datepicker.min.js',
              '/media/static/js/seleccion_fecha.js',
              )  
        css = {'all':('/media/static/css/datepicker/jquery-datepicker.css',)}
        
class VentasPorTurnoForm(VentasForm):
    'Formulario de generación reporte de ventas por turno'
    """
    sucursal = forms.ModelChoiceField(
                               queryset=Sucursal.objects.all(),
                               required=True,
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               label=u"Sucursal",
                               help_text=u"Seleccione la sucursal",
                               )    
    """     
    def __init__(self, *args, **kwargs):
        super(VentasPorTurnoForm, self).__init__(*args, **kwargs)
        self.fields['tipo'].initial = 1
        self.fields['formato'].required = False
    
    class Media:
        js = ('/media/static/js/jquery.js',
              '/media/static/js/reporte/forms/ventas_por_turno.js',
              ) 

class BuscarTurnoForm(forms.Form):
    """Busca un registro de turno dentro de una tabla"""
    class Media:
        #Se carga la magia necesaria para recargar las subcategorías vía ajax
        js = (
            '/media/static/js/jquery.quicksearch.pack.js',
            '/media/static/js/reporte/forms/buscar_turno.js',
        )


class VentaMesForm(ReporteForm):
    'Formulario de generacion de reporte de Productos'
    OPCION_MES = (
                     (1,'Enero'),
                     (2,'Febrero'),
                     (3,'Marzo'),
                     (4,'Abril'),
                     (5,'Mayo'),
                     (6,'Junio'),
                     (7,'Julio'),
                     (8,'Agosto'),
                     (9,'Septiembre'),
                     (10,'Octubre'),
                     (11,'Noviembre'),
                     (12,'Diciembre'),
                     )
    
    REPORTE_DETALLE = 1
    REPORTE_RESUMIDO = 2
    
    OPCION_REPORTE = (
                      (REPORTE_DETALLE,'Detalle'),
                      (REPORTE_RESUMIDO,'Resumen'), 
                      )
    
    def __init__(self, anios, dia, *args, **kwargs):
        super(VentaMesForm,self).__init__(*args,**kwargs)
        inicio = anios['inicio'].year
        fin = anios['fin'].year
        if inicio == fin:
            fin = inicio
        self.fields['anio'].choices = [(x,x) for x in tuple(range(inicio,fin+1))]
        self.fields['mes'].initial = dia.month
        self.fields['anio'].initial = dia.year
        
    tipo_reporte = forms.ChoiceField(
                               label=u"Tipo",
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               help_text=u"Seleccione el tipo de reporte que desea visualizar",
                               choices = OPCION_REPORTE,
                               )
    
    mes = forms.ChoiceField(
                               label=u"Mes",
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               help_text=u"Seleccione el mes",
                               choices = OPCION_MES,
                               )
    anio = forms.ChoiceField(
                               label=u"Año",
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               help_text=u"Seleccione el año",
                               )

class VentasGraficosForm(ReporteForm):
    'Formulario de generaciñon de reporte de por rango de fecha'
    
    OPCION_ELEMENTO = (
                     (1,'Productos'),
                     (2,'Promociones'),
                     )    
    
    fecha_inicio = forms.DateField(input_formats = ['%d/%m/%Y'], 
                                   widget=forms.TextInput({'class':'tipo_fecha'}),
                                   help_text=u'Seleccione el período de inicio')
    fecha_fin = forms.DateField(label=u'Fecha término',input_formats = ['%d/%m/%Y'], 
                                   widget=forms.TextInput({'class':'tipo_fecha'}),
                                help_text=u'Seleccione el período de término')
    
    elemento =forms.ChoiceField(
                               label=u"Tipo",
                               widget=forms.Select(),
                               help_text=u"Seleccione productos o promociones",
                               choices = OPCION_ELEMENTO,
                               )
    
    def __init__(self, *args, **kwargs):
        super(VentasGraficosForm, self).__init__(*args, **kwargs)
        self.fields['fecha_inicio'].initial = datetime.date.today().strftime('%d/%m/%Y')
        self.fields['fecha_fin'].initial = datetime.date.today().strftime('%d/%m/%Y')
        
    class Media:
        js = ('/media/static/js/jquery.js',
              '/media/static/js/jquery-ui-datepicker.min.js',
              '/media/static/js/reporte/ventas/seleccion_fecha.js',
              )
        css = {'all':('/media/static/css/datepicker/jquery-datepicker.css',)}
    
    def clean(self):
        """ Método de validación personalizado que válida si
        la fecha de inici sea menor que la fecha de término """
        cleaned_data = self.cleaned_data

        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")


        if fecha_inicio > fecha_fin:
            # Se ingresa la información de error.
            msg = u"La fecha de inicio debe ser menor que la fecha de término."
            self._errors["fecha_fin"] = ErrorList([msg])

            # Como estos campos ya no son válidos, entonces
            # se eliminan del diccionario de objetos válidos
            del cleaned_data["fecha_inicio"]
            del cleaned_data["fecha_fin"]

        # Se retorna el diccioario de datos limpios
        return cleaned_data 


class VentasGraficosPorCategoriaForm(ReporteForm):
    'Formulario de generaciñon de reporte de por rango de fecha'
    
    OPCION_ELEMENTO = (
                     (1,'Productos'),
                     (2,'Promociones'),
                     )    
    
    TODAS_LAS_CATEGORIAS = 0
    
    fecha_inicio = forms.DateField(input_formats = ['%d/%m/%Y'], 
                                   widget=forms.TextInput({'class':'tipo_fecha'}),
                                   help_text=u'Seleccione el período de inicio')
    fecha_fin = forms.DateField(label=u'Fecha término',input_formats = ['%d/%m/%Y'], 
                                   widget=forms.TextInput({'class':'tipo_fecha'}),
                                help_text=u'Seleccione el período de término')
    
    elemento =forms.ChoiceField(
                               label=u"Tipo",
                               widget=forms.Select(),
                               help_text=u"Seleccione productos o promociones",
                               choices = OPCION_ELEMENTO,
                               )

    categoria = forms.ChoiceField(
                               required=True,
                               label=u"Categoría",
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               help_text=u"Seleccione una categoría"
                               )

    
    def __init__(self, *args, **kwargs):
        super(VentasGraficosPorCategoriaForm, self).__init__(*args, **kwargs)
        self.fields['fecha_inicio'].initial = datetime.date.today().strftime('%d/%m/%Y')
        self.fields['fecha_fin'].initial = datetime.date.today().strftime('%d/%m/%Y')
        self.fields['categoria'].choices =[(0,'TODAS')] + [(x.id,x.__unicode__()) for x in Categoria.objects.all()]
        
    class Media:
        js = ('/media/static/js/jquery.js',
              '/media/static/js/jquery-ui-datepicker.min.js',
              '/media/static/js/reporte/ventas/seleccion_fecha.js',
              )
        css = {'all':('/media/static/css/datepicker/jquery-datepicker.css',)}
    
    def clean(self):
        """ Método de validación personalizado que válida si
        la fecha de inici sea menor que la fecha de término """
        cleaned_data = self.cleaned_data

        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")


        if fecha_inicio > fecha_fin:
            # Se ingresa la información de error.
            msg = u"La fecha de inicio debe ser menor que la fecha de término."
            self._errors["fecha_fin"] = ErrorList([msg])

            # Como estos campos ya no son válidos, entonces
            # se eliminan del diccionario de objetos válidos
            del cleaned_data["fecha_inicio"]
            del cleaned_data["fecha_fin"]

        # Se retorna el diccioario de datos limpios
        return cleaned_data
