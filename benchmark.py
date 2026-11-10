
import time
import math
import heapq
from collections import deque


# ---------------------------------------------------------------------------
# 1. Definición del Problema CampusGuard
# ---------------------------------------------------------------------------

class ProblemaCampusGuard:
    """Problema de planificación de intervenciones para un estudiante en riesgo.

    Estado: tupla (r, a, c, t, b)
        r: nivel de riesgo académico (0 a 10)
        a: inasistencias recientes (0 a 8)
        c: nivel de carga académica (1 a 4)
        t: tutorías asignadas (0 a 5)
        b: bienestar notificado (0 o 1)
    """

    COSTOS = {
        'TUTORIA': 1,
        'SEGUIMIENTO': 1,
        'ASESORIA': 2,
        'BIENESTAR': 4,
        'AJUSTE_CARGA': 5,
    }

    def __init__(self, initial=(10, 8, 4, 0, 0)):
        """Recibe el estado inicial; por defecto (10, 8, 4, 0, 0)."""
        self.initial = initial

    def actions(self, state):
        """Devuelve la lista de acciones aplicables en el estado."""
        r, a, c, t, b = state
        acciones = []
        if r > 0 and t < 5:
            acciones.append('TUTORIA')
        if a > 0:
            acciones.append('SEGUIMIENTO')
        if r > 0 and a > 0:
            acciones.append('ASESORIA')
        if b == 0:
            acciones.append('BIENESTAR')
        if c > 1 and r > 0:
            acciones.append('AJUSTE_CARGA')
        return acciones

    def result(self, state, action):
        """Modelo de transición: devuelve el estado resultante de aplicar la acción."""
        r, a, c, t, b = state
        if action == 'TUTORIA':
            return (max(r - 1, 0), a, c, t + 1, b)
        if action == 'SEGUIMIENTO':
            return (r, max(a - 1, 0), c, t, b)
        if action == 'ASESORIA':
            return (max(r - 1, 0), max(a - 1, 0), c, t, b)
        if action == 'BIENESTAR':
            return (max(r - 2, 0), max(a - 3, 0), c, t, 1)
        if action == 'AJUSTE_CARGA':
            return (max(r - 3, 0), a, max(c - 1, 1), t, b)
        raise ValueError(f'Acción desconocida: {action}')

    def goal_test(self, state):
        """Devuelve True si el estudiante alcanzó riesgo bajo (r <= 2) y asistencia regular (a <= 1)."""
        r, a, _, _, _ = state
        return r <= 2 and a <= 1

    def path_cost(self, c, state1, action, state2):
        """Devuelve el costo acumulado c más el costo de la acción."""
        return c + self.COSTOS[action]


# ---------------------------------------------------------------------------
# 2. Nodo del árbol de búsqueda
# ---------------------------------------------------------------------------

class Nodo:
    """Nodo del árbol de búsqueda: estado, padre, acción, costo g(n) y profundidad."""

    __slots__ = ('state', 'parent', 'action', 'path_cost', 'depth')

    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = parent.depth + 1 if parent else 0

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


def _resultado(nodo, expandidos, max_frontera, max_memoria, tiempo_ms):
    """Empaqueta el resultado de una búsqueda en un diccionario."""
    return {
        'nodo': nodo,
        'acciones': nodo.solucion() if nodo else None,
        'costo': nodo.path_cost if nodo else None,
        'profundidad': nodo.depth if nodo else None,
        'nodos_expandidos': expandidos,
        'max_frontera': max_frontera,
        'max_memoria': max_memoria,
        'tiempo_ms': tiempo_ms,
    }


# ---------------------------------------------------------------------------
# 3. Algoritmos de Búsqueda No Informada (BFS y DFS)
# ---------------------------------------------------------------------------

def busqueda_anchura(problema):
    """BFS en grafo con cola FIFO y conjunto de estados alcanzados."""
    t0 = time.perf_counter()
    raiz = Nodo(problema.initial)
    if problema.goal_test(raiz.state):
        t1 = time.perf_counter()
        return _resultado(raiz, 0, 1, 1, (t1 - t0) * 1000)

    frontera = deque([raiz])
    alcanzados = {raiz.state}
    expandidos = 0
    max_frontera = 1
    max_memoria = 1

    while frontera:
        nodo = frontera.popleft()
        expandidos += 1
        for hijo in nodo.expandir(problema):
            if hijo.state not in alcanzados:
                if problema.goal_test(hijo.state):
                    t1 = time.perf_counter()
                    return _resultado(hijo, expandidos, max_frontera, max_memoria, (t1 - t0) * 1000)
                alcanzados.add(hijo.state)
                frontera.append(hijo)
        max_frontera = max(max_frontera, len(frontera))
        max_memoria = max(max_memoria, len(alcanzados))

    t1 = time.perf_counter()
    return _resultado(None, expandidos, max_frontera, max_memoria, (t1 - t0) * 1000)


def busqueda_profundidad(problema):
    """DFS en grafo con pila LIFO y conjunto de estados explorados."""
    t0 = time.perf_counter()
    frontera = [Nodo(problema.initial)]
    explorados = set()
    expandidos = 0
    max_frontera = 1
    max_memoria = 1

    while frontera:
        nodo = frontera.pop()
        if problema.goal_test(nodo.state):
            t1 = time.perf_counter()
            return _resultado(nodo, expandidos, max_frontera, max_memoria, (t1 - t0) * 1000)
        if nodo.state in explorados:
            continue
        explorados.add(nodo.state)
        expandidos += 1
        en_frontera = {n.state for n in frontera}
        for hijo in nodo.expandir(problema):
            if hijo.state not in explorados and hijo.state not in en_frontera:
                frontera.append(hijo)
        max_frontera = max(max_frontera, len(frontera))
        max_memoria = max(max_memoria, len(frontera) + len(explorados))

    t1 = time.perf_counter()
    return _resultado(None, expandidos, max_frontera, max_memoria, (t1 - t0) * 1000)


# ---------------------------------------------------------------------------
# 4. Algoritmo de Búsqueda Informada (A*) y Heurística Admisible
# ---------------------------------------------------------------------------

def heuristica_admisible(state):
    """Función heurística h(n) <= h*(n) para CampusGuard.
    
    Estima el costo mínimo restante para reducir el riesgo r <= 2 y las inasistencias a <= 1.
    Dado que la acción con mayor reducción combinada por unidad de costo es BIENESTAR 
    (reduce 5 unidades de riesgo+inasistencias por un costo de 4), el costo real nunca 
    será menor a 0.8 * (dr + da).
    """
    r, a, c, t, b = state
    dr = max(0, r - 2)
    da = max(0, a - 1)
    if dr == 0 and da == 0:
        return 0
    return math.ceil(0.8 * (dr + da))


def busqueda_a_estrella(problema, h=heuristica_admisible):
    """A* Graph Search con cola de prioridad orientada por f(n) = g(n) + h(n)."""
    t0 = time.perf_counter()
    raiz = Nodo(problema.initial)
    if problema.goal_test(raiz.state):
        t1 = time.perf_counter()
        return _resultado(raiz, 0, 1, 1, (t1 - t0) * 1000)

    count = 0
    frontera = []
    heapq.heappush(frontera, (raiz.path_cost + h(raiz.state), count, raiz))
    alcanzados = {raiz.state: raiz.path_cost}
    expandidos = 0
    max_frontera = 1
    max_memoria = 1

    while frontera:
        f, _, nodo = heapq.heappop(frontera)

        if problema.goal_test(nodo.state):
            t1 = time.perf_counter()
            return _resultado(nodo, expandidos, max_frontera, max_memoria, (t1 - t0) * 1000)

        expandidos += 1

        for hijo in nodo.expandir(problema):
            s = hijo.state
            if s not in alcanzados or hijo.path_cost < alcanzados[s]:
                alcanzados[s] = hijo.path_cost
                count += 1
                f_hijo = hijo.path_cost + h(s)
                heapq.heappush(frontera, (f_hijo, count, hijo))

        max_frontera = max(max_frontera, len(frontera))
        max_memoria = max(max_memoria, len(frontera) + len(alcanzados))

    t1 = time.perf_counter()
    return _resultado(None, expandidos, max_frontera, max_memoria, (t1 - t0) * 1000)


# ---------------------------------------------------------------------------
# 5. Programa Principal y Ejecución de Experimentos Benchmark
# ---------------------------------------------------------------------------

def imprimir_resultado(nombre, resultado):
    """Muestra en consola la solución, el costo y las métricas de una búsqueda."""
    print(f'=== {nombre} ===')
    if resultado['nodo'] is None:
        print('No se encontró solución.\n')
        return
    print('Secuencia de acciones:')
    estados = resultado['nodo'].camino_estados()
    print(f'  {"":14} {estados[0]}')
    for i, (accion, estado) in enumerate(zip(resultado['acciones'], estados[1:]), 1):
        print(f'  {i:2}. {accion:12} -> {estado}')
    print(f'Número de acciones (d) : {resultado["profundidad"]}')
    print(f'Costo total g(n)       : {resultado["costo"]} horas')
    print(f'Nodos expandidos       : {resultado["nodos_expandidos"]}')
    print(f'Tiempo CPU             : {resultado["tiempo_ms"]:.3f} ms')
    print(f'Frontera máxima        : {resultado["max_frontera"]}')
    print(f'Estados en memoria     : {resultado["max_memoria"]} (máximo)\n')


if __name__ == '__main__':
    problema = ProblemaCampusGuard()
    print('=' * 80)
    print(' BENCHMARK COMPARATIVO COMPLETO - CAMPUSGUARD (FASE 2)')
    print(f' Estado inicial s0: {problema.initial}')
    print(' Meta: Riesgo (r) <= 2  e  Inasistencias (a) <= 1')
    print('=' * 80 + '\n')

    imprimir_resultado('BFS (Búsqueda en Anchura - No Informada)', busqueda_anchura(problema))
    imprimir_resultado('DFS (Búsqueda en Profundidad - No Informada)', busqueda_profundidad(problema))
    imprimir_resultado('A* (Búsqueda A Estrella - Informada)', busqueda_a_estrella(problema))
