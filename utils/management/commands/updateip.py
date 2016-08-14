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
import urllib2
import xmlrpclib
import os
from settings import DNS_DOMAIN, DNS_PASSWD, DNS_USER

class Command(NoArgsCommand):
    help = u"Actualiza la ip para que el DNS resuelva correctamente el dominio."
    
    def handle_noargs(self, **options):
         
        currentip = urllib2.urlopen('http://www.whatismyip.org').read()
         
        if not os.path.isfile('lastip'):
            f = open('lastip', 'w')
            f.close()
         
        with open('lastip', 'r') as f:
            lastip = f.read()
         
        if lastip != currentip:
            server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
            session_id, account = server.login(DNS_USER, DNS_PASSWD)
            server.delete_dns_override(session_id, DNS_DOMAIN)
            server.create_dns_override(session_id, DNS_DOMAIN, currentip, '', '', '', '')
         
            with open('lastip', 'w') as f:
                f.write(currentip)
         
            print('IP actualizada: %s' % currentip)
        else:
            print('IP sin actualizar')
