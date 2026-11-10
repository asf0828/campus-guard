
import heapq
import math


def _transiciones_relajadas(estado):
    r, a, b = estado
    sucesores = []

    if r > 0:
        sucesores.append(((max(0, r - 1), a, b), 1))

    if a > 0:
        sucesores.append(((r, max(0, a - 1), b), 1))

    if r > 0 and a > 0:
        sucesores.append(((max(0, r - 1), max(0, a - 1), b), 2))

    if b == 0:
        sucesores.append(((max(0, r - 2), max(0, a - 3), 1), 4))

    if r > 0:
        sucesores.append(((max(0, r - 3), a, b), 5))

    return sucesores


def construir_tabla_patrones():
    estados = [
        (r, a, b)
        for r in range(11)
        for a in range(9)
        for b in (0, 1)
    ]

    inverso = {estado: [] for estado in estados}

    for estado in estados:
        for siguiente, costo in _transiciones_relajadas(estado):
            inverso[siguiente].append((estado, costo))

    distancias = {
        estado: 0
        for estado in estados
        if estado[0] <= 2 and estado[1] <= 1
    }

    frontera = [(0, estado) for estado in distancias]
    heapq.heapify(frontera)

    while frontera:
        costo_actual, estado = heapq.heappop(frontera)

        if costo_actual != distancias[estado]:
            continue

        for predecesor, costo_arista in inverso[estado]:
            nuevo_costo = costo_actual + costo_arista

            if nuevo_costo < distancias.get(predecesor, math.inf):
                distancias[predecesor] = nuevo_costo
                heapq.heappush(frontera, (nuevo_costo, predecesor))

    return distancias


TABLA_PATRONES = construir_tabla_patrones()


def heuristica_admisible(state):
    r, a, _c, _t, b = state
    return TABLA_PATRONES[(r, a, b)]
