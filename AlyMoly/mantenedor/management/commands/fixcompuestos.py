#-*- encoding: UTF-8 -*-
###############################################
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@crecelibre.cl                      #
# ©Andrés Otárola Alvarado                    #
# aotarola@crecelibre.cl                      #
# 2010                                        #
###############################################

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from AlyMoly.mantenedor.models import Producto
from django.db import connection

class Command(BaseCommand):
    help = u"Corrige el atributo es_compuesto productos compuestos correspondientes."

    @transaction.atomic
    def handle(self, *args, **options):
        #Se obtienen los datos que se encuentren sin sincronizar
        compuestos_id = Producto.objects.exclude(compone=None).values_list('compone',flat=True)
        compuestos = Producto.objects.filter(id__in=compuestos_id)
        compuestos.update(es_compuesto=True)
