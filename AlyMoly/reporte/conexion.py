#-*- encoding: UTF-8 -*-'''
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
import pycurl
import StringIO

class URLRetriever(object):
    
    def __init__(self,url):
        self.url = url
    
    def get(self):
        c = pycurl.Curl()
        c.setopt(pycurl.URL, self.url.encode())
        c.setopt(pycurl.HTTPHEADER, ["Accept:"])
        b = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        try:
            c.perform()
            http_code = c.getinfo(pycurl.HTTP_CODE)
            
            if http_code == 502: #Bad Gateway
                raise pycurl.error()
            elif http_code == 401: #Permission denied
                raise pycurl.error()
        except pycurl.error:
            raise
        finally:
            c.close()
        return b.getvalue()