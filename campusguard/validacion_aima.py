"""Ejecuta las búsquedas de AIMA-Python sobre CampusGuard.

Sirve para validar la implementación propia de ``campusguard.busquedas`` con
un código externo y reconocido: si BFS y A* dan los mismos planes, costos y
nodos expandidos en ambas implementaciones, hay una buena señal de que la
propia es correcta.

``CampusGuard`` tiene la misma interfaz que ``Problem`` de AIMA (``actions``,
``result``, ``goal_test``, ``path_cost``, ``h``), así que las funciones de AIMA
se pueden aplicar sin adaptaciones.

AIMA-Python es una dependencia opcional: el resto del proyecto funciona sin
instalarla (ver la sección "Validación con AIMA-Python" del README).

Las métricas se toman con ``InstrumentedProblem`` de AIMA, que envuelve al
problema y cuenta cuántas veces se llama cada método. Su contador ``succs``
suma una unidad cada vez que el algoritmo pide las acciones de un estado, es
decir, cada vez que expande un nodo, así que equivale a los nodos expandidos
de la implementación propia. AIMA no expone el máximo de estados en memoria,
por lo que ese valor queda en ``None``.
"""

from __future__ import annotations

from typing import Callable, Optional

from campusguard.busquedas import Resultado

# La importación se intenta al cargar el módulo. Si AIMA no está instalado, el
# módulo se carga igual y ``InstrumentedProblem`` queda en ``None``, que es lo
# que revisa ``aima_disponible``. Así el resto del proyecto puede importar este
# módulo sin exigir AIMA.
try:
    from aima.search import (
        InstrumentedProblem,
        astar_search,
        breadth_first_graph_search,
        depth_first_graph_search,
    )
except ImportError:
    InstrumentedProblem = None

INSTALACION = (
    "AIMA-Python no está instalado. Instálalo, idealmente en un entorno virtual, con:\n"
    '  pip install --no-deps "git+https://github.com/aimacode/aima-python.git'
    '@49ebbc316192e84489f8bcb061e24b69150598fc"\n'
    "  pip install numpy"
)
"""Mensaje con las instrucciones de instalación, para mostrar si AIMA falta.

Se instala fijado a un commit para que los resultados sean reproducibles, y
con ``--no-deps`` porque sus dependencias declaradas incluyen paquetes de
aprendizaje automático que la búsqueda no usa; ``aima.search`` solo necesita
NumPy.
"""


def aima_disponible() -> bool:
    """Indica si AIMA-Python se pudo importar."""
    return InstrumentedProblem is not None


def _verificar() -> None:
    """Lanza ``ImportError`` con las instrucciones de instalación si AIMA no está disponible."""
    if not aima_disponible():
        raise ImportError(INSTALACION)


def _resultado(nombre: str, instrumentado, nodo) -> Resultado:
    """Traduce el resultado de AIMA (un ``Node`` o ``None``) a un ``Resultado`` propio.

    Así el benchmark muestra las filas de AIMA igual que las propias.
    ``node.solution()`` es la lista de acciones y ``node.path_cost`` su costo.
    """
    if nodo is None:
        return Resultado(nombre, False, nodos_expandidos=instrumentado.succs,
                         max_estados_en_memoria=None)
    return Resultado(nombre, True, nodo.solution(), nodo.path_cost, nodo.state,
                     instrumentado.succs, None)


def anchura_aima(problema) -> Resultado:
    """BFS en grafo de AIMA (``breadth_first_graph_search``).

    Debe coincidir con ``busqueda_anchura`` en plan, costo y nodos expandidos.
    """
    _verificar()
    instrumentado = InstrumentedProblem(problema)
    nodo = breadth_first_graph_search(instrumentado)
    return _resultado("BFS (AIMA)", instrumentado, nodo)


def profundidad_aima(problema) -> Resultado:
    """DFS en grafo de AIMA (``depth_first_graph_search``).

    Su plan difiere del de ``busqueda_profundidad``, y es lo esperado: AIMA
    apila los sucesores en el orden en que los devuelve ``actions``, así que
    explora primero la última acción, mientras que la implementación propia
    los apila al revés para explorar primero la primera. Muestra cuánto
    depende DFS del orden de las acciones.
    """
    _verificar()
    instrumentado = InstrumentedProblem(problema)
    nodo = depth_first_graph_search(instrumentado)
    return _resultado("DFS (AIMA)", instrumentado, nodo)


def a_estrella_aima(problema, h: Optional[Callable] = None,
                    nombre: str = "A* (AIMA)") -> Resultado:
    """A* de AIMA (``astar_search``) con la heurística ``h`` o, si no se indica, ``problema.h``.

    Debe coincidir con ``busqueda_a_estrella`` en costo y nodos expandidos con
    cada heurística.
    """
    _verificar()
    # La heurística se resuelve antes de envolver el problema porque
    # InstrumentedProblem hereda el h() de Problem, que devuelve 0, y ocultaría
    # la heurística configurada en CampusGuard.
    h = h or problema.h
    instrumentado = InstrumentedProblem(problema)
    nodo = astar_search(instrumentado, h)
    return _resultado(nombre, instrumentado, nodo)
