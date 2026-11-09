"""Compara la implementación propia con AIMA-Python.

Si AIMA-Python no está instalado, estas pruebas se omiten y el resto de la
suite funciona igual.
"""

import contextlib
import io
import unittest

import benchmark
from campusguard import validacion_aima
from campusguard.busquedas import busqueda_a_estrella, busqueda_anchura
from campusguard.heuristicas import HEURISTICAS, h_combinada
from campusguard.problema import CampusGuard
from tests.test_busquedas import reproducir


@unittest.skipUnless(validacion_aima.aima_disponible(), "AIMA-Python no está instalado")
class TestValidacionAima(unittest.TestCase):
    def setUp(self):
        self.problema = CampusGuard()

    def verificar_plan(self, resultado):
        estado, costo = reproducir(self.problema, resultado.acciones)
        self.assertTrue(self.problema.goal_test(estado))
        self.assertEqual(costo, resultado.costo)

    def test_bfs_coincide(self):
        propio = busqueda_anchura(self.problema)
        aima = validacion_aima.anchura_aima(self.problema)
        self.verificar_plan(aima)
        self.assertEqual(aima.acciones, propio.acciones)
        self.assertEqual(aima.nodos_expandidos, propio.nodos_expandidos)

    def test_a_estrella_coincide_con_cada_heuristica(self):
        for nombre, h in HEURISTICAS.items():
            with self.subTest(heuristica=nombre):
                propio = busqueda_a_estrella(self.problema, h=h)
                aima = validacion_aima.a_estrella_aima(self.problema, h=h)
                self.verificar_plan(aima)
                self.assertEqual(aima.costo, propio.costo)
                self.assertEqual(aima.nodos_expandidos, propio.nodos_expandidos)

    def test_a_estrella_usa_la_heuristica_del_problema(self):
        problema = CampusGuard(heuristica=h_combinada)
        self.assertEqual(validacion_aima.a_estrella_aima(problema).nodos_expandidos, 133)

    def test_dfs_explora_primero_la_ultima_accion(self):
        aima = validacion_aima.profundidad_aima(self.problema)
        self.verificar_plan(aima)
        ultima_accion = self.problema.actions(self.problema.initial)[-1]
        self.assertEqual(aima.acciones[0], ultima_accion)
        self.assertEqual((len(aima.acciones), aima.costo), (15, 22))

    def test_no_reporta_memoria(self):
        self.assertIsNone(validacion_aima.anchura_aima(self.problema).max_estados_en_memoria)

    def test_benchmark_con_aima(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            benchmark.main(["--aima", "--repeticiones", "1"])
        self.assertIn("| A* (AIMA, h combinada) | 7 | 14 | Sí | 133 | - |", salida.getvalue())


class TestSinAima(unittest.TestCase):
    def test_mensaje_de_instalacion(self):
        if validacion_aima.aima_disponible():
            self.skipTest("AIMA-Python está instalado")
        with self.assertRaises(ImportError):
            validacion_aima.anchura_aima(CampusGuard())
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                benchmark.main(["--aima", "--repeticiones", "1"])


if __name__ == "__main__":
    unittest.main()
