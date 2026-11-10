
import heapq
import itertools
import math
from collections import deque

from .heuristicas import heuristica_admisible


class Nodo:

    def __init__(
        self,
        state,
        parent=None,
        action=None,
        path_cost=0,
        depth=0
    ):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = depth

    def expandir(self, problema):
        hijos = []

        for accion in problema.actions(self.state):
            siguiente = problema.result(self.state, accion)

            nuevo_costo = problema.path_cost(
                self.path_cost,
                self.state,
                accion,
                siguiente
            )

            hijo = Nodo(
                state=siguiente,
                parent=self,
                action=accion,
                path_cost=nuevo_costo,
                depth=self.depth + 1
            )

            hijos.append(hijo)

        return hijos

    def solucion(self):
        acciones = []
        nodo = self

        while nodo.parent is not None:
            acciones.append(nodo.action)
            nodo = nodo.parent

        return list(reversed(acciones))

    def camino_estados(self):
        estados = []
        nodo = self

        while nodo is not None:
            estados.append(nodo.state)
            nodo = nodo.parent

        return list(reversed(estados))


def _resultado(nodo, expandidos, max_frontera, max_memoria):

    return {
        "nodo": nodo,
        "acciones": nodo.solucion() if nodo else None,
        "estados": nodo.camino_estados() if nodo else None,
        "costo": nodo.path_cost if nodo else None,
        "profundidad": nodo.depth if nodo else None,
        "nodos_expandidos": expandidos,
        "max_frontera": max_frontera,
        "max_memoria": max_memoria
    }


def busqueda_anchura(problema):

    raiz = Nodo(problema.initial)

    frontera = deque([raiz])
    visitados = {raiz.state}

    expandidos = 0
    max_frontera = 1
    max_memoria = 1

    while frontera:

        nodo = frontera.popleft()

        if problema.goal_test(nodo.state):
            return _resultado(
                nodo,
                expandidos,
                max_frontera,
                max_memoria
            )

        expandidos += 1

        for hijo in nodo.expandir(problema):

            if hijo.state not in visitados:

                visitados.add(hijo.state)
                frontera.append(hijo)

        max_frontera = max(max_frontera, len(frontera))
        max_memoria = max(
            max_memoria,
            len(frontera) + len(visitados)
        )

    return _resultado(None, expandidos, max_frontera, max_memoria)


def busqueda_profundidad(problema):

    raiz = Nodo(problema.initial)

    frontera = [raiz]
    visitados = set()

    expandidos = 0
    max_frontera = 1
    max_memoria = 1

    while frontera:

        nodo = frontera.pop()

        if nodo.state in visitados:
            continue

        visitados.add(nodo.state)

        if problema.goal_test(nodo.state):
            return _resultado(
                nodo,
                expandidos,
                max_frontera,
                max_memoria
            )

        expandidos += 1

        hijos = nodo.expandir(problema)

        for hijo in reversed(hijos):

            if hijo.state not in visitados:
                frontera.append(hijo)

        max_frontera = max(max_frontera, len(frontera))
        max_memoria = max(
            max_memoria,
            len(frontera) + len(visitados)
        )

    return _resultado(None, expandidos, max_frontera, max_memoria)


def busqueda_a_estrella(problema):

    contador = itertools.count()

    raiz = Nodo(problema.initial)

    frontera = [
        (heuristica_admisible(raiz.state), next(contador), raiz)
    ]

    mejor_costo = {raiz.state: 0}

    expandidos = 0
    max_frontera = 1
    max_memoria = 1

    while frontera:

        _, _, nodo = heapq.heappop(frontera)

        if nodo.path_cost != mejor_costo.get(nodo.state):
            continue

        if problema.goal_test(nodo.state):
            return _resultado(
                nodo,
                expandidos,
                max_frontera,
                max_memoria
            )

        expandidos += 1

        for accion in problema.actions(nodo.state):

            siguiente = problema.result(nodo.state, accion)

            nuevo_costo = problema.path_cost(
                nodo.path_cost,
                nodo.state,
                accion,
                siguiente
            )

            if nuevo_costo < mejor_costo.get(siguiente, math.inf):

                mejor_costo[siguiente] = nuevo_costo

                hijo = Nodo(
                    state=siguiente,
                    parent=nodo,
                    action=accion,
                    path_cost=nuevo_costo,
                    depth=nodo.depth + 1
                )

                prioridad = nuevo_costo + heuristica_admisible(
                    siguiente
                )

                heapq.heappush(
                    frontera,
                    (prioridad, next(contador), hijo)
                )

        max_frontera = max(max_frontera, len(frontera))

        max_memoria = max(
            max_memoria,
            len(frontera) + len(mejor_costo)
        )

    return _resultado(None, expandidos, max_frontera, max_memoria)


def imprimir_resultado(nombre, resultado):

    print(f"\n=== {nombre} ===")

    if resultado["nodo"] is None:
        print("No se encontró una solución.")
        return

    print("Secuencia de acciones:")

    for i, (accion, estado) in enumerate(
        zip(
            resultado["acciones"],
            resultado["estados"][1:]
        ),
        start=1
    ):
        print(f"{i:>2}. {accion:<15} -> {estado}")

    print("Número de acciones:", resultado["profundidad"])
    print("Costo total:", resultado["costo"])
    print("Nodos expandidos:", resultado["nodos_expandidos"])
    print("Frontera máxima:", resultado["max_frontera"])
    print("Memoria máxima:", resultado["max_memoria"])
