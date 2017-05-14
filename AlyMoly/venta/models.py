#!/usr/bin/env python
#-*- encoding: UTF-8 -*-

###############################################
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@minostro.com                       #
# 2009                                        #
###############################################
from django.db import models
from AlyMoly.mantenedor.models import Producto, Promocion, Trabajador


class Turno(models.Model):
    """
        estado:
            1 --> abierto
            2 --> cerrado
    """
    fecha_apertura_sistema = models.DateTimeField()
    fecha_cierre_sistema = models.DateTimeField(null=True, blank=True)
    estado = models.IntegerField(default=1, blank=True)
    trabajador = models.ForeignKey(Trabajador, blank=True)
    monto_apertura_caja = models.IntegerField(default=0)
    monto_cierre_calculado = models.IntegerField(default=0, blank=True)
    monto_afecto = models.IntegerField(default=0, blank=True)
    monto_exento = models.IntegerField(default=0, blank=True)

    def monto_cierre_informado(self):
        return self.boletadeposito.total

    def estado_turno(self):
        if self.estado == 1:
            return "Abierto"
        else:
            return "Cerrado"

    def save(self, force_insert=False, force_update=False):
        """
            Al guardar un turno abierto se verifica que el trabajador ya no cuente con un
            turno abierto anteriormente.
        """
        if self.estado == 1 and len(Turno.objects.exclude(id=self.id).filter(trabajador__id=self.trabajador.id).filter(estado=1)) > 0:
            raise Exception(u"Usted ya cuenta con un turno abierto.")
        super(Turno, self).save(force_insert, force_update)


class BoletaDeposito(models.Model):
    turno = models.OneToOneField(Turno, blank=True)
    veintemil = models.PositiveIntegerField(default=0, blank=True)
    diezmil = models.PositiveIntegerField(default=0, blank=True)
    cincomil = models.PositiveIntegerField(default=0, blank=True)
    dosmil = models.PositiveIntegerField(default=0, blank=True)
    mil = models.PositiveIntegerField(default=0, blank=True)
    quinientos = models.PositiveIntegerField(default=0, blank=True)
    cien = models.PositiveIntegerField(default=0, blank=True)
    cincuenta = models.PositiveIntegerField(default=0, blank=True)
    diez = models.PositiveIntegerField(default=0, blank=True)
    tarjetas = models.PositiveIntegerField(default=0, blank=True)
    otros = models.PositiveIntegerField(default=0, blank=True)
    total = models.PositiveIntegerField(default=0, blank=True)


class Venta(models.Model):
    """
        medio_pago:
            1 --> efectivo
            2 --> otro
    """
    fecha_venta = models.DateTimeField()
    folio_boleta = models.PositiveIntegerField(null=True, blank=True)
    monto_total = models.PositiveIntegerField()
    monto_afecto = models.PositiveIntegerField()
    monto_exento = models.PositiveIntegerField()
    cantidad_productos = models.PositiveIntegerField()
    medio_pago = models.PositiveIntegerField()
    monto_pago = models.PositiveIntegerField(null=True)
    turno = models.ForeignKey('Turno')

    def __unicode__(self):
        return u"%s-%s" % (self.id, self.folio_boleta)


class LineaDetalle(models.Model):
    cantidad = models.IntegerField()
    precio_venta = models.IntegerField()
    precio_venta_total = models.IntegerField()
    producto = models.ForeignKey(Producto, null=True, blank=True)
    promocion = models.ForeignKey(Promocion, null=True, blank=True)
    venta = models.ForeignKey('Venta')
