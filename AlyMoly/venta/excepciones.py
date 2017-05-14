#-*- encoding: UTF-8 -*-
###############################################
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@minostro.com                       #
# 2009                                        #
###############################################

class DetalleError(Exception):
    pass

class ProductoError(Exception):
    pass

class ExistenciaError(Exception):
    pass

class PromocionError(Exception):
    pass

class ElementoError(Exception):
    pass

class FactoriaError(Exception):
    pass

class AbstractaError(Exception):
    pass

class VentaError(Exception):
    pass

class SesionError(Exception):
    pass

class BodegaError(Exception):
    pass

class OperacionError(Exception):
    pass

class CajaError(Exception):
    pass

class TrabajadorError(Exception):
    pass

class TurnoError(Exception):
    pass

class TurnoMultipleError(Exception):
    pass

class ProductoExistenciaError(Exception):
    pass

class PromocionExistenciaError(Exception):
    pass

class ProductoDescuentoError(Exception):
    pass

class ProductoAumentoError(Exception):
    pass

class VentaNoExisteError(Exception):
    pass
