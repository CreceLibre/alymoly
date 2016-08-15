#-*- encoding: UTF-8 -*-
from django.http import HttpResponseNotAllowed, HttpResponseForbidden

def remote_method_only(method):
    """Verifica que la petición sea asíncrona y el método sea de tipo @method."""
    def decorator(target):
        def wrapper(*args, **kwargs):
            request = args[0]
            if not request.is_ajax() : return HttpResponseForbidden()
            if request.method == method:
                return target(*args,**kwargs)       
            return HttpResponseNotAllowed(permitted_methods=[method])
        wrapper.__doc__= target.__doc__
        wrapper.__name__= target.__name__
        return wrapper
    return decorator
