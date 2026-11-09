"""Algoritmos de búsqueda en grafo: BFS, DFS y A*.

Los tres algoritmos siguen el mismo esquema general:

1. Se guardan en una *frontera* los nodos descubiertos que falta explorar,
   empezando por el nodo del estado inicial.
2. Se saca un nodo de la frontera. Si su estado cumple la meta, se devuelve
   el camino que lleva a él.
3. Si no, se *expande*: se generan sus hijos aplicando cada acción posible y
   se agregan a la frontera los que lleven a estados nuevos.

Lo que distingue a cada algoritmo es qué nodo saca primero de la frontera:

* BFS usa una cola (FIFO): saca el más antiguo, así que explora por niveles.
* DFS usa una pila (LIFO): saca el más reciente, así que profundiza primero.
* A* usa una cola de prioridad: saca el de menor f(n) = g(n) + h(n).

Son búsquedas "en grafo" porque recuerdan los estados ya vistos para no
explorarlos dos veces cuando se llega a ellos por caminos distintos.

Los algoritmos son independientes del problema: solo usan la interfaz
``actions``, ``result``, ``goal_test``, ``path_cost`` y ``h`` definida en
``campusguard.problema.Problem``. ``Nodo`` y la estructura de cada búsqueda se
adaptan de ``Node``, ``breadth_first_graph_search``, ``depth_first_graph_search``
y ``astar_search`` de AIMA-Python
(https://github.com/aimacode/aima-python/blob/master/aima/search.py).

Todos los algoritmos reportan las mismas métricas:

* nodos expandidos: nodos a los que se les generan sus sucesores;
* estados en memoria: máximo de estados guardados a la vez entre la frontera
  y el registro de estados visitados.
"""

from __future__ import annotations

import heapq
import itertools
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class Nodo:
    """Nodo del árbol de búsqueda.

    Un estado describe la situación del estudiante; un nodo, además, recuerda
    cómo se llegó a ella: desde qué nodo (``padre``), con qué ``accion``, con
    qué ``costo`` acumulado (g(n)) y a qué ``profundidad`` (número de
    acciones). Dos nodos distintos pueden tener el mismo estado si se llega a
    él por caminos diferentes.
    """

    estado: object
    padre: Optional["Nodo"] = None
    accion: Optional[str] = None
    costo: float = 0
    profundidad: int = 0

    def expandir(self, problema) -> list["Nodo"]:
        """Genera los nodos hijos, uno por cada acción aplicable en este estado."""
        hijos = []
        for accion in problema.actions(self.estado):
            siguiente = problema.result(self.estado, accion)
            # El costo del hijo es el costo del padre más el de la acción.
            costo = problema.path_cost(self.costo, self.estado, accion, siguiente)
            hijos.append(Nodo(siguiente, self, accion, costo, self.profundidad + 1))
        return hijos

    def acciones(self) -> list[str]:
        """Reconstruye el plan: la secuencia de acciones desde la raíz hasta este nodo.

        Se sigue la cadena de padres hacia atrás y al final se invierte, porque
        se recorre del último paso al primero.
        """
        camino = []
        nodo = self
        while nodo.padre is not None:
            camino.append(nodo.accion)
            nodo = nodo.padre
        return list(reversed(camino))


@dataclass
class Resultado:
    """Resultado de una búsqueda y sus métricas.

    * ``algoritmo``: nombre del algoritmo que lo produjo.
    * ``encontrado``: si se llegó a la meta.
    * ``acciones``: el plan encontrado (vacío si no hubo solución).
    * ``costo``: costo total del plan, o ``None`` si no hubo solución.
    * ``estado_final``: estado al que llega el plan.
    * ``nodos_expandidos``: cuántos nodos se expandieron.
    * ``max_estados_en_memoria``: máximo de estados guardados a la vez.
    """

    algoritmo: str
    encontrado: bool
    acciones: list[str] = field(default_factory=list)
    costo: Optional[float] = None
    estado_final: object = None
    nodos_expandidos: int = 0
    max_estados_en_memoria: int = 0


def _resultado(algoritmo, nodo, expandidos, memoria) -> Resultado:
    """Construye el ``Resultado`` a partir del nodo meta, o de ``None`` si no hubo solución."""
    if nodo is None:
        return Resultado(algoritmo, False, nodos_expandidos=expandidos,
                         max_estados_en_memoria=memoria)
    return Resultado(algoritmo, True, nodo.acciones(), nodo.costo, nodo.estado,
                     expandidos, memoria)


def busqueda_anchura(problema) -> Resultado:
    """BFS (búsqueda en anchura) en grafo.

    Explora por niveles: primero todos los estados a una acción del inicio,
    luego los que están a dos, y así sucesivamente. Por eso la primera
    solución que encuentra es la que tiene menos acciones, aunque no
    necesariamente la de menor costo.

    Prueba la meta al *generar* cada hijo, no al sacarlo de la frontera: como
    explora por niveles, el primer hijo meta que aparece ya es uno de los
    menos profundos, y así se ahorra expandir el resto de su nivel.
    """
    raiz = Nodo(problema.initial)
    if problema.goal_test(raiz.estado):
        return _resultado("BFS", raiz, 0, 1)
    frontera = deque([raiz])        # cola FIFO: se agrega al final, se saca del inicio
    alcanzados = {raiz.estado}      # estados ya descubiertos (en la frontera o expandidos)
    expandidos = 0
    while frontera:
        nodo = frontera.popleft()   # el más antiguo: así se recorre nivel por nivel
        expandidos += 1
        for hijo in nodo.expandir(problema):
            if hijo.estado in alcanzados:
                continue            # ya se llegó a este estado por un camino igual de corto
            if problema.goal_test(hijo.estado):
                # +1 porque el estado meta también se guardó en memoria.
                return _resultado("BFS", hijo, expandidos, len(alcanzados) + 1)
            alcanzados.add(hijo.estado)
            frontera.append(hijo)
    # La frontera se vació sin encontrar la meta: no hay solución.
    return _resultado("BFS", None, expandidos, len(alcanzados))


def busqueda_profundidad(problema) -> Resultado:
    """DFS (búsqueda en profundidad) en grafo.

    Sigue cada camino hasta el fondo antes de retroceder y probar otro. Gasta
    poca memoria, porque solo guarda el camino actual y sus alternativas
    pendientes, pero la solución que encuentra depende del orden de las
    acciones y no tiene por qué ser la más corta ni la más barata. Lleva
    registro de los estados explorados para no repetirlos.
    """
    frontera = [Nodo(problema.initial)]  # pila LIFO: se agrega y se saca del final
    explorados = set()                   # estados ya expandidos
    expandidos = 0
    memoria = 1
    while frontera:
        nodo = frontera.pop()            # el más reciente: así se profundiza primero
        if problema.goal_test(nodo.estado):
            return _resultado("DFS", nodo, expandidos, memoria)
        if nodo.estado in explorados:
            continue                     # ya se expandió por otro camino
        explorados.add(nodo.estado)
        expandidos += 1
        # Los hijos se apilan en orden inverso para que el primero de la lista
        # quede arriba de la pila y se explore primero.
        frontera.extend(reversed(nodo.expandir(problema)))
        memoria = max(memoria, len(frontera) + len(explorados))
    return _resultado("DFS", None, expandidos, memoria)


def busqueda_a_estrella(problema, h: Optional[Callable] = None,
                        nombre: str = "A*") -> Resultado:
    """A* en grafo: expande primero el nodo con menor f(n) = g(n) + h(n).

    * g(n) es el costo real acumulado desde el inicio hasta n (``Nodo.costo``).
    * h(n) es la heurística: una estimación de lo que falta hasta la meta.

    f(n) estima el costo total de la mejor solución que pasa por n. Si h nunca
    sobreestima (es *admisible*) y cumple la desigualdad triangular (es
    *consistente*), el primer nodo meta que sale de la frontera es el de menor
    costo. Con h = 0, A* se comporta como búsqueda de costo uniforme: es
    óptimo, pero sin pistas sobre hacia dónde está la meta.

    Usa ``h`` si se indica y, si no, ``problema.h``. ``nombre`` es el nombre
    con el que aparece en el resultado.
    """
    h = h or problema.h
    # Desempate: si dos nodos tienen el mismo f(n), sale primero el que entró
    # antes. Además evita que heapq intente comparar dos objetos Nodo.
    contador = itertools.count()
    raiz = Nodo(problema.initial)
    # La frontera es un montículo (heap) de tuplas (f(n), orden, nodo):
    # heappop siempre devuelve la de menor f(n).
    frontera = [(h(raiz), next(contador), raiz)]
    mejor_costo = {raiz.estado: 0}  # menor g(n) conocido para cada estado
    expandidos = 0
    memoria = 1
    while frontera:
        _, _, nodo = heapq.heappop(frontera)
        # La meta se prueba al *sacar* el nodo, no al generarlo: solo entonces
        # es seguro que no queda en la frontera un camino más barato.
        if problema.goal_test(nodo.estado):
            return _resultado(nombre, nodo, expandidos, memoria)
        if nodo.costo > mejor_costo[nodo.estado]:
            # Entrada obsoleta: después de agregar este nodo se encontró un
            # camino más barato al mismo estado. En lugar de buscarlo y
            # borrarlo de la frontera (que costaría recorrerla), se deja ahí y
            # se descarta al salir. Esto se llama "borrado perezoso".
            continue
        expandidos += 1
        for hijo in nodo.expandir(problema):
            # Solo interesa el hijo si mejora el mejor camino conocido a su estado.
            if hijo.costo < mejor_costo.get(hijo.estado, float("inf")):
                mejor_costo[hijo.estado] = hijo.costo
                heapq.heappush(frontera, (hijo.costo + h(hijo), next(contador), hijo))
        memoria = max(memoria, len(mejor_costo))
    return _resultado(nombre, None, expandidos, memoria)
