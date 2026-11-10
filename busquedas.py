import heapq
from itertools import count

from .heuristicas import heuristica_admisible


def busqueda_a_estrella(problema):
 
    raiz = Nodo(problema.initial)

    if problema.goal_test(raiz.state):
        return _resultado(raiz, 0, 1, 1)

    contador = count()
    frontera = []

    heapq.heappush(
        frontera,
        (heuristica_admisible(raiz.state), next(contador), raiz)
    )

    mejores_costos = {raiz.state: 0}
    expandidos = 0
    max_frontera = 1
    max_memoria = 1

    while frontera:
        _, _, nodo = heapq.heappop(frontera)

        if nodo.path_cost > mejores_costos.get(
            nodo.state, float("inf")
        ):
            continue

        if problema.goal_test(nodo.state):
            return _resultado(
                nodo, expandidos, max_frontera, max_memoria
            )

        expandidos += 1

        for hijo in nodo.expandir(problema):
            costo_actual = mejores_costos.get(
                hijo.state, float("inf")
            )

            if hijo.path_cost < costo_actual:
                mejores_costos[hijo.state] = hijo.path_cost

                f = hijo.path_cost + heuristica_admisible(hijo.state)

                heapq.heappush(
                    frontera, (f, next(contador), hijo)
                )

        max_frontera = max(max_frontera, len(frontera))
        max_memoria = max(
            max_memoria, len(frontera) + len(mejores_costos)
        )

    return _resultado(None, expandidos, max_frontera, max_memoria)
