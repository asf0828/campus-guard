"""Búsqueda informada (A*) para el problema CampusGuard.

A* expande primero el nodo con menor f(n) = g(n) + h(n). La heurística la
aporta el problema a través de ``problema.h``, definida en ``heuristicas.py``.
"""

import heapq
import itertools
import math

from heuristicas import heuristica_admisible
from problema import ProblemaCampusGuard, Nodo


def busqueda_a_estrella(problema):
    contador = itertools.count()
    raiz = Nodo(problema.initial)

    frontera = [(problema.h(raiz), next(contador), raiz)]
    mejor_costo = {raiz.state: 0}

    expandidos = 0
    generados = 1
    max_frontera = 1
    max_memoria = 1

    while frontera:
        _prioridad, _orden, nodo = heapq.heappop(frontera)

        if nodo.path_cost != mejor_costo.get(nodo.state):
            continue

        if problema.goal_test(nodo.state):
            return {
                "nodo": nodo,
                "acciones": nodo.solucion(),
                "estados": nodo.camino_estados(),
                "costo": nodo.path_cost,
                "profundidad": nodo.depth,
                "nodos_expandidos": expandidos,
                "nodos_generados": generados,
                "max_frontera": max_frontera,
                "max_memoria": max_memoria,
            }

        expandidos += 1

        for accion in problema.actions(nodo.state):
            siguiente = problema.result(nodo.state, accion)
            nuevo_costo = problema.path_cost(
                nodo.path_cost, nodo.state, accion, siguiente
            )
            generados += 1

            if nuevo_costo < mejor_costo.get(siguiente, math.inf):
                mejor_costo[siguiente] = nuevo_costo
                hijo = Nodo(
                    state=siguiente,
                    parent=nodo,
                    action=accion,
                    path_cost=nuevo_costo,
                    depth=nodo.depth + 1,
                )
                prioridad = nuevo_costo + problema.h(hijo)
                heapq.heappush(
                    frontera, (prioridad, next(contador), hijo)
                )

        max_frontera = max(max_frontera, len(frontera))
        max_memoria = max(max_memoria, len(mejor_costo))

    return None

#EJECUCIÓN

def main():
    problema = ProblemaCampusGuard()
    resultado = busqueda_a_estrella(problema)

    print("Estado inicial:", problema.initial)
    print("Meta: r <= 2 y a <= 1")
    print("\n=== A* (BUSQUEDA INFORMADA) ===")

    if resultado is None:
        print("No se encontró una solución.")
        return

    print("Secuencia de acciones:")
    for i, (accion, estado) in enumerate(
        zip(resultado["acciones"], resultado["estados"][1:]), start=1
    ):
        print(f"{i:>2}. {accion:<15} -> {estado}")

    print("\nNúmero de acciones  :", resultado["profundidad"])
    print("Costo total g(n)    :", resultado["costo"])
    print("Nodos expandidos    :", resultado["nodos_expandidos"])
    print("Nodos generados     :", resultado["nodos_generados"])
    print("Frontera máxima     :", resultado["max_frontera"])
    print("Estados en memoria  :", resultado["max_memoria"])
    print("h(estado inicial)   :", heuristica_admisible(problema.initial))


if __name__ == "__main__":
    main()
