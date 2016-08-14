from settings import NOMBRE_SUCURSAL

def sucursal(request):
    return {'sucursal': NOMBRE_SUCURSAL}