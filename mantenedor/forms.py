#-*- encoding: UTF-8 -*-
###############################################
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@crecelibre.cl                      #
# ©Andrés Otárola Alvarado                    #
# aotarola@crecelibre.cl                      #
# 2009                                        #
###############################################
from django import forms
from mantenedor.models import Producto, Bodega, Categoria, Promocion, Proveedor, Trabajador
from django.forms.util import ErrorList
from django.contrib.localflavor.cl.forms import CLRutField
from django.core.exceptions import ObjectDoesNotExist
from utils import widgets

class ProductoForm(forms.ModelForm):
    #atributo virtual ;)
    codigo_barra = forms.RegexField(label=u"Código de barra",
                                    regex='^\*?[a-zA-Z0-9]+$',
                                    help_text=u'Debe ingresar un código de barra automático o manual',
                                    error_messages = {'invalid':u'Formato de código de barra es incorrecto'})
    
    categoria = forms.ModelChoiceField(label=u"Categoría",queryset=Categoria.objects.filter(supercategoria=None).order_by('nombre'), 
                                       widget=forms.Select(attrs={'style':'width:230px'}), required=True, 
                                       help_text=u'Seleccione la categoría que pertenece el&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br /> producto')
    subcategoria = forms.ModelChoiceField(label=u"Subcategoría",queryset=Categoria.objects.all().order_by('nombre'), 
                                       widget=forms.Select(attrs={'style':'width:230px'}), required=False, 
                                       help_text=u'Seleccione la subcategoría a la cual pertenece el producto')
    
    compuesto_por = forms.CharField(label=u"Producto",
                                    help_text=u'Debe ingresar el código de barra del producto que compone al producto actual',
                                    widget=widgets.NombreProductoSearchWidget(), required=False)
    
    cantidad_compuesto = forms.IntegerField(label=u'Cantidad',min_value=1,\
                                           required=False, help_text=u'Ingrese la cantidad que compone al producto')
    
    def __init__(self,*args,**kwargs):
        super(ProductoForm,self).__init__(*args,**kwargs)
        try:
            if kwargs['instance'].es_compuesto:
                p = Producto.objects.get(compone=kwargs['instance'].id)
                self.initial['compuesto_por'] = p.codigo_barra
                self.initial['cantidad_compuesto'] = p.cantidad_compone
        except KeyError:
            #No existe la instancia en un formulario de no-edición
            pass
        
    def clean(self):
        """ Método de validación personalizado que válida si
        el precio de costo no sea mayor que el precio de venta """
        cleaned_data = self.cleaned_data
        try:
            if cleaned_data["subcategoria"] is None:
                cleaned_data["subcategoria"] = cleaned_data["categoria"]
        except KeyError:
            msg = u"Debe seleccionar una categoría."
            self._errors["categoria"] = ErrorList([msg])
            del cleaned_data["subcategoria"]
        try:
            precio_costo = int(cleaned_data.get("precio_costo"))
            precio_venta = int(cleaned_data.get("precio_venta"))
        except (TypeError,ValueError):
            return cleaned_data

        if precio_costo >= precio_venta:
            # Se ingresa la información de error.
            msg = u"El Precio de costo debe ser menor que el precio de venta."
            self._errors["precio_costo"] = ErrorList([msg])

            # Como estos campos ya no son válidos, entonces
            # se eliminan del diccionario de objetos válidos
            del cleaned_data["precio_costo"]
            del cleaned_data["precio_venta"]
            
        if cleaned_data["es_compuesto"]: 
            
            if cleaned_data['compuesto_por'].strip() == '':
                msg = u"Debe ingresar un código de barra."
                self._errors["compuesto_por"] = ErrorList([msg])
                del cleaned_data["compuesto_por"]
            if not cleaned_data['cantidad_compuesto']:
                msg = u"Debe ingresar la cantidad que compone al producto."
                self._errors["cantidad_compuesto"] = ErrorList([msg])
                del cleaned_data["cantidad_compuesto"]
                
            if cleaned_data.has_key("compuesto_por") and cleaned_data.has_key('cantidad_compuesto'):
                try:
                    old = Producto.objects.filter(compone__codigo_barra=cleaned_data['codigo_barra'])
                    if old.count() > 0:
                        old.update(compone=None, cantidad_compone=0)
                    p = Producto.objects.get(codigo_barra=cleaned_data["compuesto_por"])
                    if p.es_compuesto:
                        msg = u"El código de barra ingresado hace referencia a un producto que ya es compuesto."
                        self._errors["compuesto_por"] = ErrorList([msg])
                        del cleaned_data["compuesto_por"]
                except ObjectDoesNotExist:
                    msg = u"El código de barra ingresado no existe."
                    self._errors["compuesto_por"] = ErrorList([msg])
                    del cleaned_data["compuesto_por"]
        else:
            old = Producto.objects.filter(compone__codigo_barra=cleaned_data['codigo_barra'])
            if old.count() > 0:
                old.update(compone=None, cantidad_compone=0)

        # Se retorna el diccionario de datos limpios
        return cleaned_data

    def clean_codigo_barra(self):
        "Verifica que campo único, quitando espacio en blanco"
        data = self.cleaned_data["codigo_barra"].replace(" ", "").lower()
        self.cleaned_data["codigo_barra"] = data
        if data != self.instance.codigo_barra.lower():
            objetos = Producto.objects.filter(codigo_barra=data).count()
            if objetos >= 1:
                raise forms.ValidationError(u"Ya existe Producto con este Código Barra.")
            objetos = Promocion.objects.filter(codigo=data).count()
            if objetos >= 1:
                raise forms.ValidationError(u"Ya existe una Promoción con este Código Barra.")            
        return data
    
    def save(self, commit=True):
        producto = super(ProductoForm, self).save(commit=False)
        producto.chavo = 8
        if producto.es_compuesto:
            producto._compuesto_por = self.cleaned_data["compuesto_por"]
            producto._cantidad_compone = self.cleaned_data["cantidad_compuesto"]
        return producto

    
    class Meta:
        model = Producto
        
    class Media:
        #Se carga la magia necesaria para recargar las subcategorías vía ajax
        js = (
            '/media/static/js/jquery.js',
            '/media/static/js/jquery.capitalize.min.js',
            '/media/static/js/mantenedor/producto/categorias.js',
        ) 


class BodegaForm(forms.ModelForm):

    def clean_ubicacion(self):
        "Verifica que campo único, quitando espacio en blanco"
        data = self.cleaned_data["ubicacion"].strip().lower()
        self.cleaned_data["ubicacion"] = data
        if data != self.instance.ubicacion.lower():
            objetos = Bodega.objects.filter(ubicacion=data).count()
            if objetos >= 1:
                raise forms.ValidationError("Ya existe Bodega con esta Ubicación.")
        return data
    
    def clean_venta(self):
        data = self.cleaned_data['venta']
        if data and len(Bodega.objects.exclude(pk=self.instance.id).filter(venta=True)) > 0:
            raise forms.ValidationError("Usted ya cuenta con una bodega de venta")
        return data

    class Meta:
        model = Bodega

        
class CategoriaForm(forms.ModelForm):

    def clean_nombre(self):
        "Verifica que campo único, quitando espacio en blanco"
        data = self.cleaned_data["nombre"].strip().lower()
        self.cleaned_data["nombre"] = data
        if data != self.instance.nombre.lower():
            objetos = Categoria.objects.filter(nombre=data).count()
            if objetos >= 1:
                raise forms.ValidationError("Ya existe Categoría con este Nombre.")
        return data

    class Meta:
        model = Categoria
        
class PromocionForm(forms.ModelForm):

    codigo = forms.RegexField(label=u"Código de barra",
                                    regex='^\*?[a-zA-Z0-9]+$',
                                    help_text=u'Debe ingresar un código de barra automático o manual',
                                    error_messages = {'invalid':u'Formato de código de barra es incorrecto'})
    
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.filter(supercategoria=None).order_by('nombre'), 
                                       widget=forms.Select(attrs={'style':'width:230px'}))    
    def clean(self):
        """ Método de validación personalizado que válida si
        el precio de costo no sea mayor que el precio de venta """
        cleaned_data = self.cleaned_data
        try:
            precio_costo = int(cleaned_data.get("precio_costo"))
            precio_venta = int(cleaned_data.get("precio_venta"))
        except (TypeError,ValueError):
            return cleaned_data

        if precio_costo >= precio_venta:
            # Se ingresa la información de error.
            msg = u"El Precio de costo debe ser menor que el precio de venta."
            self._errors["precio_costo"] = ErrorList([msg])

            # Como estos campos ya no son válidos, entonces
            # se eliminan del diccionario de objetos válidos
            del cleaned_data["precio_costo"]
            del cleaned_data["precio_venta"]

        # Se retorna el diccioario de datos limpios
        return cleaned_data

    def clean_codigo(self):
        "Verifica que campo único, quitando espacio en blanco"
        data = self.cleaned_data["codigo"].replace(" ", "").lower()
        self.cleaned_data["codigo"] = data
        if data != self.instance.codigo.lower():
            objetos = Promocion.objects.filter(codigo=data).count()
            if objetos >= 1:
                raise forms.ValidationError("Ya existe Promoción con este Código Barra.")
            objetos = Producto.objects.filter(codigo_barra=data).count()
            if objetos >= 1:
                raise forms.ValidationError("Ya existe Producto con este Código Barra.")            
        return data

    
    class Meta:
        model = Promocion
        
    class Media:
        #Se carga la magia necesaria para recargar las subcategorías vía ajax
        js = (
            '/media/static/js/jquery.js',
            '/media/static/js/mantenedor/promocion/producto_promocion.js',
        )

class ProveedorForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        super(ProveedorForm,self).__init__(*args,**kwargs)
        try:
            self.initial['rut'] = unicode(kwargs['instance'].rut) + kwargs['instance'].dv   
        except KeyError:
            #No existe la instancia en un formulario de no-edición
            pass
    
    rut = CLRutField(label=u"R.U.T.",
                        help_text=u"Ingrese el rut por \
                        ejemplo: 16056807-1",
                        widget = widgets.RutWidget())
       
    def clean_rut(self):
        """
        Valida que no exista el rut ingresado
        y devuelvo el rut en su forma entera
        """        
        rut = int(self.cleaned_data['rut'][:-2].replace('.',''))
        objs = Proveedor.objects.filter(rut=rut)
        if self.instance.id:
            objs = objs.exclude(rut=self.instance.rut)
        if objs.count() > 0:
            raise forms.ValidationError(u'El rut ingresado ya existe.')
        return rut
    
    def clean_razon_social(self):
        """
        Valida que no exista a razon social ingresada
        """        
        if self.cleaned_data['razon_social'] != self.instance.razon_social:
            try:
                Proveedor.objects.get(razon_social__exact=self.cleaned_data['razon_social'])
            except ObjectDoesNotExist:
                return self.cleaned_data['razon_social']
            raise forms.ValidationError(u'La razon social ingresada ya existe.')
        return self.cleaned_data['razon_social']
    
    class Meta:
        model = Proveedor

class TrabajadorForm(forms.ModelForm):    
    def __init__(self,*args,**kwargs):
        super(TrabajadorForm,self).__init__(*args,**kwargs)
        try:
            self.initial['cedula_identidad'] = unicode(kwargs['instance'].cedula_identidad) + kwargs['instance'].digito_verificador
            self.initial['estado'] = kwargs['instance'].user.is_active
            self.fields['cedula_identidad'].widget.attrs['readonly'] = True       
        except KeyError:
            #No existe la instancia en un formulario de no-edición
            pass
    
    cedula_identidad = CLRutField(label=u"Cédula de identidad",
                        help_text=u"Ingrese la cédula de identidad por \
                        ejemplo: 16056807-1", widget = widgets.RutWidget())
    
    estado = forms.BooleanField(label=u"Estado",initial=True,
                                help_text=u"Especifique el estado que el trabajador tiene.\
                                Por defecto el trabajador está habilitado.",required=False)
       
    def clean_cedula_identidad(self):
        """
        Valida que no exista el rut ingresado
        y devuelvo el rut en su forma entera
        """        
        rut = int(self.cleaned_data['cedula_identidad'][:-2].replace('.',''))
        trabajadores = Trabajador.objects.filter(cedula_identidad=rut)
        if self.instance.id:
            trabajadores = trabajadores.exclude(cedula_identidad=self.instance.cedula_identidad)
        if trabajadores.count() > 0:
            raise forms.ValidationError(u'La cédula de identidad ingresada ya existe.')
        return rut
        
    class Meta:
        model = Trabajador