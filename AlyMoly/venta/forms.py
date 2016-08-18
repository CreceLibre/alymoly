#!/usr/bin/env python
#-*- encoding: UTF-8 -*-

###############################################
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnolog�as Ltda. #
#                                             #
# �Milton Inostroza Aguilera                  #
# minostro@crecelibre.cl                      #
# 2009                                        #
###############################################
from django import forms
from localflavor.cl.forms import CLRutField
from AlyMoly.venta import models
from AlyMoly.utils import widgets

class AutentificacionForm(forms.Form):
    cedula_identidad = CLRutField(label=u"Cédula de identidad",
                                  widget = widgets.RutWidget(),
                                  help_text=u"Ingrese su cédula de identidad incluyendo el digito verificador.  Ej.: 16056865-3")

class TurnoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TurnoForm,self).__init__(*args,**kwargs)
        self.fields['fecha_apertura_sistema'].required = False

    class Meta:
        model = models.Turno
        exclude = ['trabajador']

    class Media:
        js = (
            '/media/js/jquery.js',
            "/media/js/sucursal/sucursal.js",
            '/media/static/js/jquery.jclock.js',
        )



class CerrarTurnoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CerrarTurnoForm,self).__init__(*args,**kwargs)
        self.fields['fecha_cierre_sistema'].required = False
        self.fields['fecha_apertura_sistema'].required = False
        self.fields['monto_apertura_caja'].required = False

    class Meta:
        model = models.Turno
        exclude = ['trabajador']

    class Media:
        js = (
            '/media/js/jquery.js',
            '/media/static/js/venta/cerrar_turno.js',
            '/media/js/sucursal/sucursal.js',
            '/media/static/js/jquery.jclock.js',
        )

class BoletaDepositoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BoletaDepositoForm,self).__init__(*args, **kwargs)
        self.set_up_fields('veintemil',**{'required':True,'label':u'CLP $20.000.-'})
        self.set_up_fields('diezmil',**{'required':True,'label':u'CLP $10.000.-'})
        self.set_up_fields('cincomil',**{'required':True,'label':u'CLP $5.000.-'})
        self.set_up_fields('dosmil',**{'required':True,'label':u'CLP $2.000.-'})
        self.set_up_fields('mil',**{'required':True,'label':u'CLP $1.000.-'})
        self.set_up_fields('quinientos',**{'required':True,'label':u'CLP $500.-'})
        self.set_up_fields('cien',**{'required':True,'label':u'CLP $100.-'})
        self.set_up_fields('cincuenta',**{'required':True,'label':u'CLP $50.-'})
        self.set_up_fields('diez',**{'required':True,'label':u'CLP $10.-'})
        self.set_up_fields('tarjetas',**{'required':True,'label':u'Tarjetas'})
        self.set_up_fields('otros',**{'required':True,'label':u'Otros'})
        self.fields['total'].required = True
        self.fields['total'].widget.attrs['readonly'] = True


    def set_up_fields(self, a_field, **kwargs):
        self.fields[a_field].required = kwargs['required']
        self.fields[a_field].label = kwargs['label']
        self.fields[a_field].widget.attrs['class'] = 'boleta'

    def clean_veintemil(self):
        veintemil = int(self.cleaned_data['veintemil'])
        if not veintemil%20000 == 0:
            raise forms.ValidationError(u'Debe ingresar una cantidad múltiplo de 20.000.-')
        return self.cleaned_data['veintemil']

    def clean_diezmil(self):
        diezmil = int(self.cleaned_data['diezmil'])
        if not diezmil%10000 == 0:
            raise forms.ValidationError(u'Debe ingresar una cantidad múltiplo de 10.000.-')
        return self.cleaned_data['diezmil']

    def clean_cincomil(self):
        cincomil = int(self.cleaned_data['cincomil'])
        if not cincomil%5000 == 0:
            raise forms.ValidationError(u'Debe ingresar una cantidad múltiplo de 5.000.-')
        return self.cleaned_data['cincomil']

    def clean_dosmil(self):
        dosmil = int(self.cleaned_data['dosmil'])
        if not dosmil%2000 == 0:
            raise forms.ValidationError(u'Debe ingresar una cantidad múltiplo de 2.000.-')
        return self.cleaned_data['dosmil']

    def clean_mil(self):
        mil = int(self.cleaned_data['mil'])
        if not mil%1000 == 0:
            raise forms.ValidationError(u'Debe ingresar una cantidad múltiplo de 1.000.-')
        return self.cleaned_data['mil']

    def clean_quinientos(self):
        quinientos = int(self.cleaned_data['quinientos'])
        if not quinientos%500 == 0:
            raise forms.ValidationError(u'Debe ingresar una cantidad múltiplo de 500.-')
        return self.cleaned_data['quinientos']

    def clean_cien(self):
        cien = int(self.cleaned_data['cien'])
        if not cien%100 == 0:
            raise forms.ValidationError(u'Debe ingresar una cantidad múltiplo de 100.-')
        return self.cleaned_data['cien']

    def clean_cincuenta(self):
        cincuenta = int(self.cleaned_data['cincuenta'])
        if not cincuenta%50 == 0:
            raise forms.ValidationError(u'Debe ingresar una cantidad múltiplo de 50.-')
        return self.cleaned_data['cincuenta']

    def clean_diez(self):
        diez = int(self.cleaned_data['diez'])
        if not diez%10 == 0:
            raise forms.ValidationError(u'Debe ingresar una cantidad múltiplo de 10.-')
        return self.cleaned_data['diez']

    def clean(self):
        suma_ = 0
        try:
            suma_ += self.cleaned_data.get('veintemil')
            suma_ += self.cleaned_data.get('diezmil')
            suma_ += self.cleaned_data.get('cincomil')
            suma_ += self.cleaned_data.get('dosmil')
            suma_ += self.cleaned_data.get('mil')
            suma_ += self.cleaned_data.get('quinientos')
            suma_ += self.cleaned_data.get('cien')
            suma_ += self.cleaned_data.get('cincuenta')
            suma_ += self.cleaned_data.get('diez')
            suma_ += self.cleaned_data.get('tarjetas')
            suma_ += self.cleaned_data.get('otros')
        except TypeError:
            return self.cleaned_data
        if not suma_ == int(self.cleaned_data['total']):
            raise forms.ValidationError(u'Total no coincide con el valor que usted ha ingresado')
        return self.cleaned_data


    class Meta:
        model = models.BoletaDeposito
        fields = '__all__'

    class Media:
        js = (
            '/media/static/js/jquery.form.js',
            '/media/js/jquery.alphanumeric.pack.js',
            '/media/js/jquery-ui-highlight.min.js'
        )
