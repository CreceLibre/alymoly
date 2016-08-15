#-*- encoding: UTF-8 -*-
from django import forms
from AlyMoly.mantenedor.models import Producto

class NombreProductoForm(forms.Form):

    codigo_barra = forms.CharField()

    def clean_codigo_barra(self):
        "Verifica que exista el producto"
        data = self.cleaned_data["codigo_barra"]
        try:
            Producto.objects.get(codigo_barra=data)
        except Producto.DoesNotExist:
            raise forms.ValidationError("No existe el producto con el código de barra ingresado.")
        return data
