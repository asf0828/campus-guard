"""Pruebas exhaustivas de admisibilidad y consistencia de las heurísticas."""

import unittest

from campusguard.busquedas import busqueda_a_estrella
from campusguard.heuristicas import HEURISTICAS, h_combinada, h_maxima, h_nula
from campusguard.problema import ESTADO_INICIAL, CampusGuard
from tests.utilidades import estados_alcanzables


def costo_optimo_desde(estado) -> float:
    """h*(n): costo real mínimo hasta la meta, con búsqueda de costo uniforme."""
    resultado = busqueda_a_estrella(CampusGuard(estado), h=h_nula)
    return resultado.costo if resultado.encontrado else float("inf")


class TestHeuristicas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Se calcula una sola vez para todas las pruebas: los estados
        # alcanzables y el costo real h*(n) desde cada uno.
        cls.problema = CampusGuard()
        cls.estados = estados_alcanzables(cls.problema)
        cls.h_estrella = {s: costo_optimo_desde(s) for s in cls.estados}

    def test_admisibles(self):
        """h(n) <= h*(n) en todos los estados alcanzables."""
        for nombre, h in HEURISTICAS.items():
            for estado in self.estados:
                with self.subTest(heuristica=nombre, estado=estado):
                    self.assertLessEqual(h(estado), self.h_estrella[estado])

    def test_consistentes(self):
        """h(n) <= c(n, a, n') + h(n') para toda transición."""
        for nombre, h in HEURISTICAS.items():
            for estado in self.estados:
                for accion in self.problema.actions(estado):
                    siguiente = self.problema.result(estado, accion)
                    costo = self.problema.path_cost(0, estado, accion, siguiente)
                    with self.subTest(heuristica=nombre, estado=estado, accion=accion):
                        self.assertLessEqual(h(estado), costo + h(siguiente))

    def test_valen_cero_en_la_meta(self):
        # En la meta no falta nada, así que una heurística admisible debe dar 0.
        metas = [s for s in self.estados if self.problema.goal_test(s)]
        self.assertTrue(metas)
        for h in HEURISTICAS.values():
            for estado in metas:
                self.assertEqual(h(estado), 0)

    def test_valores_en_el_estado_inicial(self):
        self.assertEqual(self.h_estrella[ESTADO_INICIAL], 14)
        self.assertEqual(h_maxima(ESTADO_INICIAL), 8)
        self.assertEqual(h_combinada(ESTADO_INICIAL), 14)

    def test_a_estrella_optimo_con_todas(self):
        for nombre, h in HEURISTICAS.items():
            with self.subTest(heuristica=nombre):
                self.assertEqual(busqueda_a_estrella(self.problema, h=h).costo, 14)

    def test_mejor_heuristica_expande_menos(self):
        # Cuanto más se acerca h(n) al costo real, menos nodos expande A*.
        expandidos = {
            nombre: busqueda_a_estrella(self.problema, h=h).nodos_expandidos
            for nombre, h in HEURISTICAS.items()
        }
        self.assertEqual(expandidos, {"nula": 464, "maxima": 220, "combinada": 133})

    def test_heuristica_configurada_en_el_problema(self):
        problema = CampusGuard(heuristica=h_combinada)
        self.assertEqual(busqueda_a_estrella(problema).nodos_expandidos, 133)


if __name__ == "__main__":
    unittest.main()
