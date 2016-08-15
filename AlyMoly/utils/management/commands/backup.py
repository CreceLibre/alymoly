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
from settings import ROOT, BACKUP_BASE_NAME, BACKUP_REMOTE_PATH, \
                     BACKUP_HOST_USER, BACKUP_HOST_PASSWD, \
                     BACKUP_HOST, BACKUP_PORT, DATABASE_NAME, \
                     DATABASE_USER, DATABASE_HOST, DATABASE_ENGINE, \
                     DATABASE_PASSWORD, BACKUP_TOOL
import os
import paramiko
import subprocess
import bz2
import datetime

FULL_BACKUP_NAME = "%s-%s" % (BACKUP_BASE_NAME,datetime.date.today().strftime('%m-%d-%Y'))
FULL_BACKUP_COMPRESSED_NAME = FULL_BACKUP_NAME + ".bz2"
FULL_BACKUP_REMOTE_PATH = BACKUP_REMOTE_PATH + FULL_BACKUP_COMPRESSED_NAME
FULL_BACKUP_PATH = ROOT(FULL_BACKUP_NAME)
FULL_COMPRESSED_BACKUP_PATH = ROOT(FULL_BACKUP_COMPRESSED_NAME)

class Command(NoArgsCommand):
    help = u"Realiza respaldo de la base de datos actual."

    def handle_noargs(self, **options):
        
        #Inicio el respaldo de datos
        self.backup_data()
        
        #Inicio la compresión del respaldo realizado
        self.compress(FULL_BACKUP_PATH,FULL_COMPRESSED_BACKUP_PATH, remove_in=True)
        
        #Inicio la conexión sftp para trasladar el repsaldo local al servidor de respaldos
        paramiko.util.log_to_file(ROOT('paramiko.log'))
        
        transport = paramiko.Transport((BACKUP_HOST,BACKUP_PORT))
        transport.connect(username=BACKUP_HOST_USER, password=BACKUP_HOST_PASSWD)
        
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(FULL_COMPRESSED_BACKUP_PATH,FULL_BACKUP_REMOTE_PATH)
        
        sftp.close()
        transport.close()
        os.remove(FULL_COMPRESSED_BACKUP_PATH)
    
    def backup_pg(self,path):
        """Realiza respaldo de una base de datos en postgresql"""
        with open(ROOT(path),"w") as f :
            os.environ['PGPASSWORD']=DATABASE_PASSWORD
            subprocess.call([BACKUP_TOOL,
                            DATABASE_NAME,
                            "-h%s"%DATABASE_HOST,
                            "-U%s"%DATABASE_USER], stdout=f)
            
    def backup_data(self):
        if DATABASE_ENGINE == 'postgresql_psycopg2':
            self.backup_pg(FULL_BACKUP_PATH)
        else:
            raise NotImplementedError("No se ha implementado procedimiento de respaldo para el adaptador %s"%
                                      DATABASE_ENGINE)
    
    def compress(self,file_in, file_out = None, remove_in = False):
        
        data = open(file_in, 'r').read()
        
        output = bz2.BZ2File(file_out, 'wb', compresslevel=9)
        try:
            output.write(data)
        finally:
            output.close()
        if remove_in: os.remove(file_in)
