import heapq
import itertools
import math
from dataclasses import dataclass

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

@dataclass
class Nodo:
    state: tuple
    parent: object = None
    action: str = None
    path_cost: int = 0
    depth: int = 0

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

