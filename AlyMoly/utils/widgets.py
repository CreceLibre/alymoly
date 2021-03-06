#-*- encoding: UTF-8 -*-
from django import forms

class NombreProductoWidget(forms.TextInput):
    def __init__(self):
        super(NombreProductoWidget,self).__init__(attrs={'class':'codigo_barra'})

    class Media:
        js = ( '/media/js/jquery.js',
            '/media/js/jquery.capitalize.min.js',
            '/media/js/widgets/nombre_producto/descripcion.js',)

class NombreProductoSearchWidget(forms.TextInput):
    def __init__(self):
        super(NombreProductoSearchWidget,self).__init__(attrs={'class':'codigo_barra_busqueda'})

    class Media:
        js = ( '/media/js/jquery.js',
            '/media/js/jquery.capitalize.min.js',
            '/media/js/widgets/nombre_producto/descripcion_busqueda.js',)

class RutWidget(forms.TextInput):
    def __init__(self):
        super(RutWidget,self).__init__(attrs={'class':'_rut'})

    class Media:
        js = ( '/media/js/jquery.js',
               '/media/js/jquery.Rut.min.js',
               '/media/js/widgets/rut/formato.js',)
