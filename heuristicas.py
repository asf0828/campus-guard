

from heapq import heappop, heappush
from itertools import product


def construir_tabla_heuristica():
    
    estados = list(product(range(11), range(9), range(2)))
    transiciones_inversas = {estado: [] for estado in estados}

    for r, a, b in estados:
        origen = (r, a, b)
        acciones = []

        if r > 0:
            acciones.append(((max(r - 1, 0), a, b), 1))  # TUTORIA
            acciones.append(((max(r - 3, 0), a, b), 5))  # AJUSTE_CARGA

        if a > 0:
            acciones.append(((r, max(a - 1, 0), b), 1))  # SEGUIMIENTO

        if r > 0 and a > 0:
            acciones.append(
                ((max(r - 1, 0), max(a - 1, 0), b), 2)
            )  # ASESORIA

        if b == 0:
            acciones.append(
                ((max(r - 2, 0), max(a - 3, 0), 1), 4)
            )  # BIENESTAR

        for destino, costo in acciones:
            transiciones_inversas[destino].append((origen, costo))

    distancias = {}

    frontera = []
    for estado in estados:
        r, a, b = estado
        if r <= 2 and a <= 1:
            distancias[estado] = 0
            heappush(frontera, (0, estado))

    while frontera:
        costo_actual, estado = heappop(frontera)

        if costo_actual > distancias[estado]:
            continue

        for anterior, costo in transiciones_inversas[estado]:
            nuevo_costo = costo_actual + costo

            if nuevo_costo < distancias.get(anterior, float("inf")):
                distancias[anterior] = nuevo_costo
                heappush(frontera, (nuevo_costo, anterior))

    return distancias


TABLA_HEURISTICA = construir_tabla_heuristica()


def heuristica_admisible(state):
    """Devuelve una estimacion admisible del costo restante hasta la meta."""
    r, a, c, t, b = state
    return TABLA_HEURISTICA[(r, a, b)]
