#-*- encoding: UTF-8 -*-
from django import forms
from AlyMoly.mantenedor.models import Bodega
from AlyMoly.movimiento.models import ProductoBodega, Ingreso, Producto, Egreso, Traspaso
from AlyMoly.utils import widgets

class IngresoMercaderiaForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        super(IngresoMercaderiaForm,self).__init__(*args,**kwargs)
        try:
            self.initial['bodega'] = unicode(kwargs['instance'].existencia.bodega.id)
            self.initial['existencia'] = unicode(kwargs['instance'].existencia.producto.codigo_barra)
        except KeyError:
            #No existe la instancia en un formulario de no-edición
            pass

    bodega = forms.ModelChoiceField(
                               required=True,
                               label=u"Bodega",
                               queryset=Bodega.objects.all(),
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               help_text=u"Seleccione la Bodega"
                               )

    existencia = forms.CharField(label=u"Producto",
                                 widget=widgets.NombreProductoWidget())

    def clean(self):
        cleaned_data = self.cleaned_data
        bodega = cleaned_data.get("bodega")
        producto = cleaned_data.get("existencia")

        if bodega and producto:
            cleaned_data["existencia"] = ProductoBodega.objects.get(bodega=bodega,producto=producto)

        return cleaned_data

    def clean_existencia(self):
        "Verifica que exista el codigo de barra de existencia"
        data = self.cleaned_data["existencia"]
        try:
            producto = Producto.objects.get(codigo_barra=data)
            return producto
        except:
            raise forms.ValidationError(u"No existe el código de barra ingresado.")


    class Meta:
        model = Ingreso
        fields = '__all__'

class EgresoMercaderiaForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        super(EgresoMercaderiaForm,self).__init__(*args,**kwargs)
        try:
            self.initial['bodega'] = unicode(kwargs['instance'].existencia.bodega.id)
            self.initial['existencia'] = unicode(kwargs['instance'].existencia.producto.codigo_barra)
        except KeyError:
            #No existe la instancia en un formulario de no-edición
            pass

    bodega = forms.ModelChoiceField(
                               required=True,
                               label=u"Bodega",
                               queryset=Bodega.objects.all(),
                               widget=forms.Select(attrs={'style':'width:230px'}),
                               help_text=u"Seleccione la Bodega"
                               )

    existencia = forms.CharField(label=u"Producto",
                                 widget=widgets.NombreProductoWidget())

    def clean_existencia(self):
        "Verifica que exista el codigo de barra de existencia"
        data = self.cleaned_data["existencia"]
        try:
            producto = Producto.objects.get(codigo_barra=data)
            return producto
        except:
            raise forms.ValidationError(u"No existe el código de barra ingresado.")

    def clean(self):
        """ Valida lo siguiente:
        - Evita descontar mas existencias de la que existen en bodega
        - Soporta el egreso de productos compuestos
        """
        cleaned_data = self.cleaned_data
        bodega = cleaned_data.get("bodega")
        producto = cleaned_data.get("existencia")
        cantidad = cleaned_data.get("cantidad")
        if bodega and producto and cantidad:
            cleaned_data["existencia"] = ProductoBodega.objects.get(bodega=bodega,producto=producto)
            registro = None
            try:
                registro = ProductoBodega.objects.get(bodega=bodega,producto__compone=producto)
                total = registro.existencia - (registro.producto.cantidad_compone * cantidad)
            except ProductoBodega.DoesNotExist:
                registro = ProductoBodega.objects.get(bodega=bodega,producto=producto)
                total = registro.existencia - cantidad
            if total < 0 and not self.instance.id:
                del cleaned_data['cantidad']
                raise forms.ValidationError(u"No hay existencias suficientes para realizar el egreso desde la bodega.")

        return cleaned_data

    class Meta:
        model = Egreso
        fields = '__all__'

class TraspasoForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        super(TraspasoForm,self).__init__(*args,**kwargs)
        try:
            if kwargs['instance']:
                self.initial['producto'] = unicode(kwargs['instance'].producto.codigo_barra)
        except KeyError:
            #No existe la instancia en un formulario de no-edición
            pass

    producto = forms.CharField(label=u'Producto',
                               widget=widgets.NombreProductoWidget())

    def clean(self):
        """Valida lo siguiente
        -bodegas seleccionadas son distintas
        -bodega de origen tiene existencias suficientes"""
        cleaned_data = self.cleaned_data
        origen = cleaned_data.get("origen")
        destino = cleaned_data.get("destino")
        producto = cleaned_data.get("producto")
        cantidad = cleaned_data.get("cantidad")

        if origen and destino and producto and cantidad:
            if origen == destino:
                raise forms.ValidationError(u"Debe seleccionar bodegas distintas.")
            registro = None
            try:
                registro = ProductoBodega.objects.get(bodega=origen,producto__compone=producto)
                total = registro.existencia - (registro.producto.cantidad_compone * cantidad)
            except ProductoBodega.DoesNotExist:
                registro = ProductoBodega.objects.get(bodega=origen,producto=producto)
                total = registro.existencia - cantidad
            if total < 0 and not self.instance.id:
                raise forms.ValidationError(u"No hay existencias suficientes para traspasar desde la bodega de origen \"%s\"." % origen)

        # Se retorna el diccioario de datos limpios
        return cleaned_data

    def clean_producto(self):
        value = self.cleaned_data['producto']
        try:
            return Producto.objects.get(codigo_barra=value)
        except Producto.DoesNotExist:
            raise forms.ValidationError(u'No existe el producto de código de barra "%s".' % value)

    class Meta:
        model = Traspaso
        fields = '__all__'
