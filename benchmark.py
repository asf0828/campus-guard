"""Benchmark de BFS, DFS y A* sobre el mismo estado inicial de CampusGuard.

Importa el problema y los algoritmos de sus módulos, para medir exactamente
el código del proyecto: BFS y DFS de ``busqueda_no_informada.py`` y A* de
``busqueda_informada.py``, con la heurística de ``heuristicas.py``.
"""

import timeit

from problema import ProblemaCampusGuard
from busqueda_no_informada import busqueda_anchura, busqueda_profundidad
from busqueda_informada import busqueda_a_estrella

REPETICIONES = 100
"""Ejecuciones por ronda: una sola búsqueda dura menos de un milisegundo, así
que el tiempo se promedia sobre muchas para que no sea solo ruido."""


def medir(busqueda, problema):
    """Ejecuta ``busqueda`` y agrega al resultado su tiempo promedio en milisegundos.

    Se hacen cinco rondas de ``REPETICIONES`` ejecuciones y se toma la más
    rápida, que es la menos afectada por otros procesos del sistema.
    """
    resultado = busqueda(problema) or {'nodo': None}
    rondas = timeit.repeat(lambda: busqueda(problema), number=REPETICIONES, repeat=5)
    resultado['tiempo_ms'] = min(rondas) / REPETICIONES * 1000
    return resultado


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

    imprimir_resultado('BFS (Búsqueda en Anchura - No Informada)', medir(busqueda_anchura, problema))
    imprimir_resultado('DFS (Búsqueda en Profundidad - No Informada)', medir(busqueda_profundidad, problema))
    imprimir_resultado('A* (Búsqueda A Estrella - Informada)', medir(busqueda_a_estrella, problema))
