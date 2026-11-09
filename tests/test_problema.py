"""Pruebas del modelo: acciones, transiciones, meta y propiedades del espacio."""

import unittest

from campusguard.problema import (
    AJUSTE_CARGA,
    ASESORIA,
    BIENESTAR,
    COSTOS,
    ESTADO_INICIAL,
    SEGUIMIENTO,
    TUTORIA,
    CampusGuard,
)
from tests.utilidades import estados_alcanzables


class TestAcciones(unittest.TestCase):
    """Qué acciones se ofrecen en cada estado, según sus condiciones."""

    def setUp(self):
        self.problema = CampusGuard()

    def test_estado_inicial_permite_todas_las_acciones(self):
        self.assertEqual(
            set(self.problema.actions(ESTADO_INICIAL)),
            {TUTORIA, SEGUIMIENTO, ASESORIA, BIENESTAR, AJUSTE_CARGA},
        )

    def test_condiciones_de_aplicacion(self):
        # El primer estado no cumple ninguna condición; cada uno de los
        # siguientes incumple exactamente la de la acción que se revisa.
        acciones = self.problema.actions((0, 0, 1, 5, 1))
        self.assertEqual(acciones, [])
        self.assertNotIn(TUTORIA, self.problema.actions((5, 3, 2, 5, 0)))
        self.assertNotIn(BIENESTAR, self.problema.actions((5, 3, 2, 0, 1)))
        self.assertNotIn(AJUSTE_CARGA, self.problema.actions((5, 3, 1, 0, 0)))
        self.assertNotIn(ASESORIA, self.problema.actions((5, 0, 2, 0, 0)))

    def test_accion_no_aplicable_lanza_error(self):
        with self.assertRaises(ValueError):
            self.problema.result((5, 3, 2, 5, 0), TUTORIA)


class TestTransiciones(unittest.TestCase):
    """Efecto de cada acción sobre el estado y su costo."""

    def setUp(self):
        self.problema = CampusGuard()

    def test_efectos(self):
        s = (6, 5, 3, 1, 0)
        self.assertEqual(self.problema.result(s, TUTORIA), (5, 5, 3, 2, 0))
        self.assertEqual(self.problema.result(s, SEGUIMIENTO), (6, 4, 3, 1, 0))
        self.assertEqual(self.problema.result(s, ASESORIA), (5, 4, 3, 1, 0))
        self.assertEqual(self.problema.result(s, BIENESTAR), (4, 2, 3, 1, 1))
        self.assertEqual(self.problema.result(s, AJUSTE_CARGA), (3, 5, 2, 1, 0))

    def test_ningun_valor_baja_de_cero(self):
        # BIENESTAR quita 2 de riesgo y 3 de faltas aunque quede menos.
        self.assertEqual(self.problema.result((1, 2, 2, 0, 0), BIENESTAR), (0, 0, 2, 0, 1))
        self.assertEqual(self.problema.result((2, 0, 2, 0, 1), AJUSTE_CARGA), (0, 0, 1, 0, 1))

    def test_costo_de_camino(self):
        for accion, costo in COSTOS.items():
            self.assertEqual(self.problema.path_cost(10, None, accion, None), 10 + costo)


class TestMeta(unittest.TestCase):
    """La meta solo depende del riesgo y de las inasistencias."""

    def test_prueba_de_meta(self):
        problema = CampusGuard()
        self.assertTrue(problema.goal_test((2, 1, 4, 0, 0)))
        self.assertTrue(problema.goal_test((0, 0, 1, 5, 1)))
        self.assertFalse(problema.goal_test((3, 1, 4, 0, 0)))
        self.assertFalse(problema.goal_test((2, 2, 4, 0, 0)))
        self.assertFalse(problema.goal_test(ESTADO_INICIAL))


class TestValidacion(unittest.TestCase):
    """Un estado mal formado se rechaza al crear el problema."""

    def test_estado_fuera_de_rango(self):
        for estado in [(11, 0, 1, 0, 0), (0, 9, 1, 0, 0), (0, 0, 0, 0, 0),
                       (0, 0, 1, 6, 0), (0, 0, 1, 0, 2), [10, 8, 4, 0, 0]]:
            with self.assertRaises(ValueError):
                CampusGuard(estado)


class TestEspacioDeEstados(unittest.TestCase):
    """Cifras de control del modelo documentadas en AGENTS.md."""

    def setUp(self):
        self.problema = CampusGuard()
        self.estados = estados_alcanzables(self.problema)

    def test_cantidad_de_estados_alcanzables(self):
        self.assertEqual(len(self.estados), 935)

    def test_sin_ciclos(self):
        # r + a + c + (1 - b) disminuye estrictamente con cada acción.
        def potencial(s):
            r, a, c, _, b = s
            return r + a + c + (1 - b)

        for estado in self.estados:
            for accion in self.problema.actions(estado):
                siguiente = self.problema.result(estado, accion)
                self.assertLess(potencial(siguiente), potencial(estado))

    def test_factor_de_ramificacion_maximo(self):
        # b en el análisis de complejidad: máximo de acciones en un estado.
        self.assertEqual(max(len(self.problema.actions(s)) for s in self.estados), 5)


if __name__ == "__main__":
    unittest.main()
