"""Búsqueda no informada (BFS y DFS) para el problema CampusGuard.

El problema sigue la interfaz de la clase Problem de AIMA-Python y los
algoritmos se adaptan de breadth_first_graph_search y
depth_first_graph_search:
https://github.com/aimacode/aima-python/blob/master/search.py

Los algoritmos no conocen los detalles de CampusGuard: solo usan
actions, result, goal_test y path_cost.
"""

from collections import deque

from problema import ProblemaCampusGuard, Nodo


def _resultado(nodo, expandidos, max_frontera, max_memoria):
    """Empaqueta el resultado de una búsqueda en un diccionario."""
    return {
        'nodo': nodo,
        'acciones': nodo.solucion() if nodo else None,
        'costo': nodo.path_cost if nodo else None,
        'profundidad': nodo.depth if nodo else None,
        'nodos_expandidos': expandidos,
        'max_frontera': max_frontera,
        'max_memoria': max_memoria,
    }


# ---------------------------------------------------------------------------
# Búsqueda en anchura (BFS)
# ---------------------------------------------------------------------------

def busqueda_anchura(problema):
    """BFS en grafo con cola FIFO y conjunto de estados alcanzados.

    La prueba de meta se aplica al generar cada hijo (prueba temprana),
    como en AIMA. Un nodo cuenta como expandido cuando se generan sus
    sucesores. Devuelve un diccionario con el camino, su costo y las métricas.
    """
    raiz = Nodo(problema.initial)
    if problema.goal_test(raiz.state):
        return _resultado(raiz, 0, 1, 1)

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
                    return _resultado(hijo, expandidos, max_frontera, max_memoria)
                alcanzados.add(hijo.state)
                frontera.append(hijo)
        max_frontera = max(max_frontera, len(frontera))
        max_memoria = max(max_memoria, len(alcanzados))

    return _resultado(None, expandidos, max_frontera, max_memoria)


# ---------------------------------------------------------------------------
# Búsqueda en profundidad (DFS)
# ---------------------------------------------------------------------------

def busqueda_profundidad(problema):
    """DFS en grafo con pila LIFO y conjunto de estados explorados.

    El conjunto de explorados evita reexpandir estados repetidos y, por tanto,
    impide ciclos. La prueba de meta se aplica al sacar el nodo de la pila.
    Devuelve un diccionario con el camino, su costo y las métricas.
    """
    frontera = [Nodo(problema.initial)]
    explorados = set()
    expandidos = 0
    max_frontera = 1
    max_memoria = 1

    while frontera:
        nodo = frontera.pop()
        if problema.goal_test(nodo.state):
            return _resultado(nodo, expandidos, max_frontera, max_memoria)
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

    return _resultado(None, expandidos, max_frontera, max_memoria)


# ---------------------------------------------------------------------------
# Programa principal
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
    print(f'Número de acciones  : {resultado["profundidad"]}')
    print(f'Costo total g(n)    : {resultado["costo"]}')
    print(f'Nodos expandidos    : {resultado["nodos_expandidos"]}')
    print(f'Frontera máxima     : {resultado["max_frontera"]}')
    print(f'Estados en memoria  : {resultado["max_memoria"]} (máximo)\n')


if __name__ == '__main__':
    problema = ProblemaCampusGuard()
    print(f'Estado inicial: {problema.initial}')
    print('Meta: r <= 2 y a <= 1\n')
    imprimir_resultado('BFS (Búsqueda en Anchura)', busqueda_anchura(problema))
    imprimir_resultado('DFS (Búsqueda en Profundidad)', busqueda_profundidad(problema))