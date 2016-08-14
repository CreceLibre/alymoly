#-*- encoding: UTF-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from admin_tools.menu.models import Menu, MenuItem, AppListMenuItem

# to activate your custom menu add the following to your settings.py:
#
# ADMIN_TOOLS_MENU = 'Central.menu.CustomMenu' 

class CustomMenu(Menu):
    """
    Custom Menu for Central admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children.append(MenuItem(
            title=_('Dashboard'),
            url=reverse('admin:index')
        ))
        self.children.append(AppListMenuItem(
            title=_('Applications'),
            exclude_list=('django.contrib',),
        ))
        self.children.append(MenuItem(
            title=_('Inventario'),
            children = [
                        MenuItem(title=_('Inventario actual'),url=reverse('inventario:actual')),
                        MenuItem(title=_('Reiniciar Inventario'),url=reverse('inventario:reiniciar')),
                        MenuItem(title=u'Stock Critico',url=reverse('inventario:criticos')),
                        ]
        ))
        self.children.append(MenuItem(
            title=_('Reportes'),
            children = [
                        MenuItem(title=_('General'),children=[
                                                             MenuItem(title=_('Productos'), url=reverse('reporte:productos')),
                                                             MenuItem(title=_('Existencias'), url=reverse('reporte:existencias')),
                                                             ]),
                        MenuItem(title=_('Ventas'),children=[
                                                             MenuItem(title=_('Diarias'), url=reverse('reporte:ventas')),
                                                             MenuItem(title=_('Mensuales'), url=reverse('reporte:ventas_mes')),
                                                             ]),
                        MenuItem(title=u'Estadísticas',children=[
                                                             MenuItem(title=_('Ventas'), url=reverse('reporte:ventas_graficos_periodo_categoria')),
                                                             ]),
                        ]
        ))



    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        pass
