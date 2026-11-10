"""Problema CampusGuard y nodo del árbol de búsqueda.

Este módulo es la base común de las búsquedas: ``busqueda_no_informada.py``
(BFS y DFS) y ``busqueda_informada.py`` (A*) importan de aquí el problema y
el nodo. La heurística vive en ``heuristicas.py`` y el problema la expone en
su método ``h``.
"""

from heuristicas import heuristica_admisible


class ProblemaCampusGuard:
    inicial = (10, 8, 4, 0, 0)

    costos = {
        "TUTORIA": 1,
        "SEGUIMIENTO": 1,
        "ASESORIA": 2,
        "BIENESTAR": 4,
        "AJUSTE_CARGA": 5,
    }

    def __init__(self, initial=None):
        self.initial = self.inicial if initial is None else tuple(initial)

    def actions(self, state):
        r, a, c, t, b = state
        acciones = []
        if r > 0 and t < 5:
            acciones.append("TUTORIA")
        if a > 0:
            acciones.append("SEGUIMIENTO")
        if r > 0 and a > 0:
            acciones.append("ASESORIA")
        if b == 0:
            acciones.append("BIENESTAR")
        if c > 1 and r > 0:
            acciones.append("AJUSTE_CARGA")
        return acciones

    def result(self, state, action):
        r, a, c, t, b = state
        if action == "TUTORIA":
            return (max(0, r - 1), a, c, t + 1, b)
        if action == "SEGUIMIENTO":
            return (r, max(0, a - 1), c, t, b)
        if action == "ASESORIA":
            return (max(0, r - 1), max(0, a - 1), c, t, b)
        if action == "BIENESTAR":
            return (max(0, r - 2), max(0, a - 3), c, t, 1)
        if action == "AJUSTE_CARGA":
            return (max(0, r - 3), a, c - 1, t, b)
        raise ValueError(f"Acción desconocida: {action}")

    def goal_test(self, state):
        r, a, _, _, _ = state
        return r <= 2 and a <= 1

    def path_cost(self, cost_so_far, state1, action, state2):
        return cost_so_far + self.costos[action]

    def h(self, node):
        state = node.state if hasattr(node, "state") else node
        return heuristica_admisible(state)


# ---------------------------------------------------------------------------
# Nodo del árbol de búsqueda
# ---------------------------------------------------------------------------

class Nodo:
    """Nodo del árbol de búsqueda: estado, padre, acción, costo g(n) y profundidad."""

    __slots__ = ('state', 'parent', 'action', 'path_cost', 'depth')

    def __init__(self, state, parent=None, action=None, path_cost=0, depth=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        # Si no se indica, la profundidad es la del padre más uno.
        self.depth = depth if depth is not None else (parent.depth + 1 if parent else 0)

    def expandir(self, problema):
        """Genera y devuelve los nodos hijos aplicando cada acción posible."""
        hijos = []
        for accion in problema.actions(self.state):
            siguiente = problema.result(self.state, accion)
            costo = problema.path_cost(self.path_cost, self.state, accion, siguiente)
            hijos.append(Nodo(siguiente, self, accion, costo))
        return hijos

    def solucion(self):
        """Devuelve la secuencia de acciones desde la raíz hasta este nodo."""
        acciones = []
        nodo = self
        while nodo.parent is not None:
            acciones.append(nodo.action)
            nodo = nodo.parent
        return list(reversed(acciones))

    def camino_estados(self):
        """Devuelve la secuencia de estados desde la raíz hasta este nodo."""
        estados = []
        nodo = self
        while nodo is not None:
            estados.append(nodo.state)
            nodo = nodo.parent
        return list(reversed(estados))
