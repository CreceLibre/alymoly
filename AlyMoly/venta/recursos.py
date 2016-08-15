#!/usr/bin/env python
#-*- encoding: UTF-8 -*-

###############################################
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnolog�as Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@crecelibre.cl                      #
# 2009                                        #
###############################################

def calcular_dv(a_ci):
    """calcula el dv de un ci chileno"""
    ci = unicode(a_ci)
    suma  = 0
    multi = 2
    for r in ci[::-1]:
        suma  += int(r) * multi
        multi += 1
        if multi == 8:
            multi = 2
    return u'0123456789K0'[11 - suma % 11]


def get_ci_dv(a_cedula):
    """
        Metodo que retorna la cédula de identidad separada por ci y dv
    """
    cedula = a_cedula.replace(".","")
    return cedula.split('-')


def formato_miles(a_precio):
    """
        Metodo que retorna a_precio formateado en miles.
    """    
    a_precio = str(a_precio)
    if len(a_precio) < 4:
        return a_precio
    precio_ = ''
    for i in range(3,len(a_precio),3):
        if i == 3:
            precio_ = a_precio[-3:]
        else:
            precio_ = a_precio[-i:-i+3] + '.' + precio_
    precio_ = a_precio[:-i] + '.' + precio_
    return precio_


def formato_dinero(a_precio):
    """
        Metodo que retorna a_precio en formato de dinero.
    """    
    precio_ = formato_miles(a_precio) if a_precio else '0'
    inicio_ = 'CLP$ '
    termino_ = ".-"
    return inicio_ + precio_ + termino_