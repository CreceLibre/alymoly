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

from django.core.management.base import NoArgsCommand
from django.db import transaction
from mantenedor.models import Producto
from django.db import connection

class Command(NoArgsCommand):
    help = u"Corrige el atributo es_compuesto productos compuestos correspondientes."
    
    @transaction.commit_manually
    def handle_noargs(self, **options):
        try:
            #Se obtienen los datos que se encuentren sin sincronizar
            compuestos_id = Producto.objects.exclude(compone=None).values_list('compone',flat=True)
            compuestos = Producto.objects.filter(id__in=compuestos_id)
            compuestos.update(es_compuesto=True)
            transaction.commit()
        except:
            transaction.rollback()
            raise #levanto la última excepción
        finally:
            connection.close()
            