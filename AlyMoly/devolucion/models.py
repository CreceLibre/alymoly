from django.db import models
from AlyMoly.mantenedor.models import Producto, Promocion, Trabajador
from AlyMoly.venta.models import Turno

class Devolucion(models.Model):
    fecha_devolucion = models.DateTimeField()
    monto_total = models.PositiveIntegerField()
    monto_unidad = models.PositiveIntegerField()
    cantidad_productos = models.PositiveIntegerField()
    producto = models.ForeignKey(Producto, null=True)
    promocion = models.ForeignKey(Promocion, null=True)
    turno = models.ForeignKey(Turno)

    def __unicode__(self):
        return u"%s-%s"%(self.id, self.fecha_devolucion)
