"""Pruebas de BFS, DFS y A* sobre un grafo pequeño y sobre CampusGuard."""

import unittest

import itertools

from campusguard.busquedas import (
    busqueda_a_estrella,
    busqueda_anchura,
    busqueda_profundidad,
)
from campusguard.problema import ESTADO_INICIAL, CampusGuard, Problem


class GrafoPequeno(Problem):
    """Grafo dirigido con costos, para probar los algoritmos sin CampusGuard.

    A -> B (1), A -> C (5), B -> D (1), C -> D (1), D -> E (1), C -> E (1)
    El camino más corto en acciones es A-C-E (costo 6); el más barato es
    A-B-D-E (costo 3).
    """

    ARISTAS = {
        "A": {"B": 1, "C": 5},
        "B": {"D": 1},
        "C": {"D": 1, "E": 1},
        "D": {"E": 1},
        "E": {},
        "X": {},
    }

    def actions(self, state):
        # Las acciones son los nombres de los nodos vecinos.
        return list(self.ARISTAS[state])

    def result(self, state, action):
        # Moverse al vecino "X" deja al agente en el nodo "X".
        return action

    def path_cost(self, c, state1, action, state2):
        # El costo de cada paso es el peso de la arista.
        return c + self.ARISTAS[state1][action]


def reproducir(problema, acciones):
    """Aplica las acciones desde el estado inicial y devuelve estado y costo."""
    estado, costo = problema.initial, 0
    for accion in acciones:
        siguiente = problema.result(estado, accion)
        costo = problema.path_cost(costo, estado, accion, siguiente)
        estado = siguiente
    return estado, costo


class TestGrafoPequeno(unittest.TestCase):
    """Comportamiento de cada algoritmo en un grafo donde el resultado se puede verificar a mano."""

    def test_bfs_encuentra_el_camino_con_menos_acciones(self):
        r = busqueda_anchura(GrafoPequeno("A", "E"))
        self.assertEqual(r.acciones, ["C", "E"])
        self.assertEqual(r.costo, 6)

    def test_dfs_encuentra_un_camino_valido(self):
        r = busqueda_profundidad(GrafoPequeno("A", "E"))
        self.assertTrue(r.encontrado)
        self.assertEqual(r.estado_final, "E")

    def test_a_estrella_encuentra_el_camino_mas_barato(self):
        r = busqueda_a_estrella(GrafoPequeno("A", "E"))
        self.assertEqual(r.acciones, ["B", "D", "E"])
        self.assertEqual(r.costo, 3)

    def test_meta_inalcanzable(self):
        for buscar in (busqueda_anchura, busqueda_profundidad, busqueda_a_estrella):
            r = buscar(GrafoPequeno("A", "X"))
            self.assertFalse(r.encontrado)
            self.assertIsNone(r.costo)

    def test_estado_inicial_es_meta(self):
        for buscar in (busqueda_anchura, busqueda_profundidad, busqueda_a_estrella):
            r = buscar(GrafoPequeno("E", "E"))
            self.assertTrue(r.encontrado)
            self.assertEqual(r.acciones, [])
            self.assertEqual(r.costo, 0)


class TestCampusGuard(unittest.TestCase):
    """Resultados de cada algoritmo sobre el problema real."""

    def setUp(self):
        self.problema = CampusGuard()

    def verificar_plan(self, resultado):
        """Comprueba que el plan reportado llegue de verdad a la meta con el costo reportado."""
        estado, costo = reproducir(self.problema, resultado.acciones)
        self.assertTrue(self.problema.goal_test(estado))
        self.assertEqual(estado, resultado.estado_final)
        self.assertEqual(costo, resultado.costo)

    def test_bfs(self):
        r = busqueda_anchura(self.problema)
        self.verificar_plan(r)
        self.assertEqual(len(r.acciones), 6)  # solución menos profunda, d = 6
        self.assertEqual(r.costo, 17)
        self.assertEqual(r.nodos_expandidos, 127)

    def test_dfs(self):
        r = busqueda_profundidad(self.problema)
        self.verificar_plan(r)
        self.assertEqual(len(r.acciones), 8)
        self.assertEqual(r.costo, 23)
        self.assertEqual(r.nodos_expandidos, 8)

    def test_a_estrella_sin_heuristica_es_optimo(self):
        r = busqueda_a_estrella(self.problema)
        self.verificar_plan(r)
        self.assertEqual(r.costo, 14)
        self.assertEqual(r.nodos_expandidos, 464)

    def test_metricas_de_memoria(self):
        # BFS guarda niveles completos; DFS solo el camino actual y sus alternativas.
        bfs = busqueda_anchura(self.problema)
        dfs = busqueda_profundidad(self.problema)
        self.assertGreater(bfs.max_estados_en_memoria, dfs.max_estados_en_memoria)


class CampusGuardOrdenado(CampusGuard):
    """CampusGuard con las acciones devueltas en otro orden.

    Las condiciones y los efectos no cambian: solo se reordena la lista que
    devuelve ``actions``, para ver cómo afecta a cada algoritmo.
    """

    def __init__(self, orden):
        super().__init__()
        self.orden = orden

    def actions(self, state):
        disponibles = set(super().actions(state))
        return [accion for accion in self.orden if accion in disponibles]


class TestOrdenDeAcciones(unittest.TestCase):
    """Lo que cada algoritmo garantiza no depende del orden de las acciones.

    Se prueban los 120 órdenes posibles de las cinco acciones. El orden solo
    decide cómo se desempata entre soluciones equivalentes.
    """

    @classmethod
    def setUpClass(cls):
        acciones = CampusGuard().actions(ESTADO_INICIAL)  # las cinco acciones
        cls.problemas = [CampusGuardOrdenado(orden)
                         for orden in itertools.permutations(acciones)]

    def test_hay_120_ordenes(self):
        self.assertEqual(len(self.problemas), 120)

    def test_bfs_siempre_encuentra_el_plan_mas_corto(self):
        costos = set()
        for problema in self.problemas:
            r = busqueda_anchura(problema)
            self.assertEqual(len(r.acciones), 6)
            costos.add(r.costo)
        # Hay planes de 6 acciones que cuestan 16 y otros que cuestan 17:
        # BFS no distingue entre ellos y ninguno es el óptimo (14).
        self.assertEqual(costos, {16, 17})

    def test_dfs_siempre_encuentra_un_plan_valido(self):
        costos = set()
        for problema in self.problemas:
            r = busqueda_profundidad(problema)
            self.assertTrue(problema.goal_test(r.estado_final))
            costos.add(r.costo)
        # Sin garantías: el costo varía mucho según el orden.
        self.assertEqual((min(costos), max(costos)), (15, 24))

    def test_a_estrella_siempre_encuentra_el_optimo(self):
        for problema in self.problemas:
            self.assertEqual(busqueda_a_estrella(problema).costo, 14)


if __name__ == "__main__":
    unittest.main()
