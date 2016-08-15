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
from settings import ROOT
from string import Template
import sys
class Command(NoArgsCommand):
    help = u"Imprime reglas de tareas cron."
    
    def handle_noargs(self, **options):
        cwd = ROOT('')
        crontab = Template("""
# Tarea de respaldo de datos
59 23,15 * * * cd $cwd ; python manage.py backup
# Tarea de actualización de IP
*/5 * * * * cd $cwd ; python manage.py updateip
""").substitute(cwd=cwd).strip()
        sys.stdout.write(crontab+'\n')