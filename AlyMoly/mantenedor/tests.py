#-*- encoding: UTF-8 -*-
from django.test import TestCase
from mantenedor.models import Categoria, Producto, Bodega
from django.db import IntegrityError, transaction

class ProductoTestCase(TestCase):
    "Pruebas para el modelo Producto"
    def setUp(self):
        vino = Categoria.objects.create(nombre="vino")
        vino.categoria_set.create(nombre="gran reserva")
        self.gran_reserva = Categoria.objects.get(nombre="gran reserva")
        self.merlot = Producto.objects.create(codigo_barra='132313',
                                              codigo_manual=False,
                                              nombre='merlot',
                                              marca='merlot',
                                              tipo_envase='botella',
                                              capacidad='250cc',
                                              precio_costo='120',
                                              precio_venta='180',
                                              exento_iva=False,
                                              cantidad_compone=0,
                                              compone=None,
                                              stock_critico = 9,
                                              subcategoria=self.gran_reserva)

    def testUnique(self):
        "Prueba de campos únicos: Producto.codigo_barra"
        self.assertRaises(IntegrityError,
                         Producto.objects.create,
                         codigo_barra='132313',
                          codigo_manual=False,
                          nombre='gato blanco',
                          marca='gato',
                          tipo_envase='caja',
                          capacidad='250cc',
                          precio_costo='120',
                          precio_venta='180',
                          exento_iva=False,
                          cantidad_compone=0,
                          compone=None,
                          subcategoria=self.gran_reserva)
        
        transaction.rollback()

class CategoriaTestCase(TestCase):
    "Pruebas para el modelo Categoria"
    def setUp(self):
        self.vino = Categoria.objects.create(nombre="vino")
    
    def testRelacion(self):
        "Prueba de relación recursiva: Categoria.supercategoria"
        self.vino.categoria_set.create(nombre="gran reserva")
        self.vino.categoria_set.create(nombre="reserva")
        self.assertEqual(self.vino.categoria_set.count(),2)
        
    def testUnique(self):
        "Prueba de campos únicos: Categoria.nombre"
        self.assertRaises(IntegrityError,
                         Categoria.objects.create,
                         nombre="vino")
        
        transaction.rollback()

class ViewsTestCase(TestCase):
    "Pruebas para las Views"
    fixtures = ['categorias.json']
    def testCategorias(self):
        #self.client.login(username='admin',password='admin')
        response = self.client.get('/admin/subcategorias/1/')
        self.assertEqual(response.status_code,200)
        #self.assertEqual(response.content,'[{"pk": 2, "model": "mantenedor.categoria", "fields": {"nombre": "gran reserva"}}]')


