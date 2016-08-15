#-*- encoding: UTF-8 -*-
import urllib
from AlyMoly.reporte.excepciones import AbstractClassException
from AlyMoly.settings import REPORT_HOST, REPORT_PORT, REPORT_APP, REPORT_DIR,\
                     NOMBRE_SUCURSAL, CANTIDAD_PRODUCTOS_MAS_VENDIDOS,\
                    CANTIDAD_PROMOCIONES_MAS_VENDIDAS
from AlyMoly.reporte.conexion import URLRetriever
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from HTMLParser import HTMLParser
import htmlentitydefs

class HTMLReportFixer(HTMLParser):
    """Cambia el título de una página html, a un titulo más institucional"""
    def __init__(self):
        HTMLParser.__init__(self)
        self.flag = False
        self.pieces = []

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.flag = True
        if tag == 'img':
            new_attrs = []
            for k,v in attrs:
                if k == 'src':
                    v = v.replace('/birt/preview',reverse('reporte:get_birt_img'))
                    new_attrs.append((k,v.encode()))
            attrs = new_attrs
        strattrs = "".join([' %s="%s"' % (key, value) for key, value in attrs])
        self.pieces.append("<%(tag)s%(strattrs)s>" % locals())

    def handle_endtag(self, tag):
        if tag == 'title':
            self.flag = False
        self.pieces.append("</%(tag)s>" % locals())

    def handle_data(self, data):
        if self.flag:
            data = "Reporte | %s" % (NOMBRE_SUCURSAL)
        self.pieces.append("%(data)s" % locals())

    def handle_charref(self,ref):
        self.pieces.append("&#%(ref)s;" % locals())

    def handle_comment(self, text):
        self.pieces.append("<!--%(text)s-->" % locals())

    def handle_entityref(self, ref):
        self.pieces.append("&%(ref)s" % locals())
        if htmlentitydefs.entitydefs.has_key(ref):
            self.pieces.append(";")

    def handle_pi(self, text):
        self.pieces.append("<?%(text)s>" % locals())

    def handle_decl(self, text):
        self.pieces.append("<!%(text)s>" % locals())

    def output(self):
        return "".join(self.pieces).replace("\n",'').strip()

class Reporte(object):
    """Clase abstracta padre que implementa la representacion un reporte genérico de
    archivo de reporte"""

    HTML = 'html'
    PDF = 'pdf'
    FORMATO = ( HTML, PDF )

    def __new__(self, *args):
        if self is Reporte :
            raise AbstractClassException
        return object.__new__(self)

    def __init__(self,data):
        self.extension = "rptdesign"
        self.params = {}
        self.formato = data['formato']
    def __unicode__(self):
        return self.nombre + '.' + self.extension

    def get_url_params(self):
        list_params = []
        for key,val in self.params.items():
            list_params.append(key + "=" + urllib.quote(str(val)))
        url_params = "&".join(list_params)
        if url_params != '':
            return "&"+url_params
        return ''

    def get_filename(self):
        return "%s.%s" % (self.nombre,self.extension)

    def get_url(self):
        return ("http://%s:%s/%s/preview?__format=%s&__report=%s%s" % (REPORT_HOST,
                                                               REPORT_PORT,
                                                               REPORT_APP,
                                                               self.formato,
                                                               REPORT_DIR, self.get_filename())) + self.get_url_params()
    def get_response(self):
        retriever = URLRetriever(self.get_url())
        response = None
        if self.formato == 'pdf':
            response = HttpResponse(retriever.get(),mimetype='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=%s.pdf' % self.__class__.__name__
        else:
            parser = HTMLReportFixer()
            parser.feed(retriever.get())
            response = HttpResponse(parser.output())
        return response

class ReportePeriodoTiempo(Reporte):

    def __new__(self, *args):
        if self is ReportePeriodoTiempo :
            raise AbstractClassException
        return object.__new__(self)

    def __init__(self,data):
        super(ReportePeriodoTiempo,self).__init__(data)
        fecha_inicio = 'fecha_inicio'
        fecha_fin = 'fecha_fin'
        if data.get('fecha',False):
            fecha_inicio = fecha_fin = 'fecha'
        self.params.update({'fecha_inicio':data[fecha_inicio].strftime('%Y-%m-%d'),
                            'fecha_fin':data[fecha_fin].strftime('%Y-%m-%d')})

##########       REPORTES        ##########

class Productos(Reporte):

    def __init__(self,data):
        super(Productos,self).__init__(data)
        self.nombre = "Productos"

class ProductosCodigoBarra(Reporte):

    def __init__(self,data):
        super(ProductosCodigoBarra,self).__init__(data)
        self.nombre = "ProductosCodigoBarra"

class ProductosCodigoManual(Reporte):

    def __init__(self,data):
        super(ProductosCodigoManual,self).__init__(data)
        self.nombre = "ProductosCodigoManual"

class ProductosExentos(Reporte):

    def __init__(self,data):
        super(ProductosExentos,self).__init__(data)
        self.nombre = "ProductosExentos"

class ProductosAfectos(Reporte):

    def __init__(self,data):
        super(ProductosAfectos,self).__init__(data)
        self.nombre = "ProductosAfectos"

class Promociones(Reporte):

    def __init__(self,data):
        super(Promociones,self).__init__(data)
        self.nombre = "Promociones"

class Existencias(Reporte):

    def __init__(self,data):
        super(Existencias,self).__init__(data)
        self.nombre = "Existencias"
        self.params.update({
                            'bodega_id':data['bodega'],
                            })

class ExistenciaPorCategoria(Reporte):

    def __init__(self,data):
        super(ExistenciaPorCategoria,self).__init__(data)
        self.nombre = "ExistenciasPorCategoria"
        self.params.update({
                            'bodega_id':data['bodega'],
                            'categoria_id':data['categoria']
                            })

class VentasPorTurno(Reporte):

    def __init__(self,data):
        super(VentasPorTurno,self).__init__(data)
        self.nombre = "EstadoDeTurno"
        self.params.update({
                            'turno_id':data['turno'],
                            })

class VentasPorTurnoDetalle(Reporte):

    def __init__(self,data):
        super(VentasPorTurnoDetalle,self).__init__(data)
        self.nombre = "VentasPorTurno"
        self.params.update({
                            'turno_id':data['turno'],
                            })

class VentasPorTurnoResumenAfectos(Reporte):

    def __init__(self,data):
        super(VentasPorTurnoResumenAfectos,self).__init__(data)
        self.nombre = "VentasPorTurnoResumenAfectos"
        self.params.update({
                            'turno_id':data['turno'],
                            })
class VentasPorTurnoResumenExentos(Reporte):

    def __init__(self,data):
        super(VentasPorTurnoResumenExentos,self).__init__(data)
        self.nombre = "VentasPorTurnoResumenExentos"
        self.params.update({
                            'turno_id':data['turno'],
                            })
class VentasPorTurnoResumenDevoluciones(Reporte):

    def __init__(self,data):
        super(VentasPorTurnoResumenDevoluciones,self).__init__(data)
        self.nombre = "VentasPorTurnoResumenDevoluciones"
        self.params.update({
                            'turno_id':data['turno'],
                            })
class VentasPorTurnoResumenPromociones(Reporte):

    def __init__(self,data):
        super(VentasPorTurnoResumenPromociones,self).__init__(data)
        self.nombre = "VentasPorTurnoResumenPromociones"
        self.params.update({
                            'turno_id':data['turno'],
                            })
class VentasPorTurnoResumenStockCritico(Reporte):

    def __init__(self,data):
        super(VentasPorTurnoResumenStockCritico,self).__init__(data)
        self.nombre = "VentasPorTurnoResumenStockCritico"
        self.params.update({
                            'turno_id':data['turno'],
                            })

class VentasPorMes(Reporte):

    def __init__(self,data):
        super(VentasPorMes,self).__init__(data)
        self.nombre = "VentaPorMes"
        fecha = data['anio'] + '-' + data['mes'] + '-01'
        self.params.update({
                            'mes_turno':fecha,
                            })

class VentasGraficoProducto(ReportePeriodoTiempo):

    def __init__(self,data):
        super(VentasGraficoProducto,self).__init__(data)
        self.nombre = "VentaGraficoProductosPorFechaPorCategorias"
        self.params.update({
                            'cantidad':CANTIDAD_PRODUCTOS_MAS_VENDIDOS,
                            })

class VentasGraficoPromocion(ReportePeriodoTiempo):

    def __init__(self,data):
        super(VentasGraficoPromocion,self).__init__(data)
        self.nombre = "VentaGraficoPromocionesPorFechaPorCategorias"
        self.params.update({
                            'cantidad':CANTIDAD_PRODUCTOS_MAS_VENDIDOS,
                            })

class VentasGraficoProductoPorCategoria(ReportePeriodoTiempo):

    def __init__(self,data):
        super(VentasGraficoProductoPorCategoria,self).__init__(data)
        self.nombre = "VentaGraficoProductosPorFechaPorCategoria"
        self.params.update({
                            'cantidad':CANTIDAD_PROMOCIONES_MAS_VENDIDAS,
                            'categoria_id':data.get("categoria"),
                            })

class VentasGraficoPromocionPorCategoria(ReportePeriodoTiempo):

    def __init__(self,data):
        super(VentasGraficoPromocionPorCategoria,self).__init__(data)
        self.nombre = "VentaGraficoPromocionesPorFechaPorCategoria"
        self.params.update({
                            'cantidad':CANTIDAD_PROMOCIONES_MAS_VENDIDAS,
                            'categoria_id':data.get("categoria"),
                            })

class VentasPorMesResumido(Reporte):

    def __init__(self,data):
        super(VentasPorMesResumido,self).__init__(data)
        self.nombre = "VentaPorMesResumido"
        fecha = data['anio'] + '-' + data['mes'] + '-01'
        self.params.update({
                            'mes_turno':fecha,
                            })
