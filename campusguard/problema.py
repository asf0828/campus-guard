"""Definición del problema de búsqueda de CampusGuard.

Un problema de búsqueda se describe con cinco elementos: un estado inicial,
las acciones posibles en cada estado, el modelo de transición (qué estado
resulta de aplicar una acción), la prueba de meta y la función de costo. Este
módulo los define en dos niveles:

* ``Problem`` es una clase base abstracta con la interfaz de ``Problem`` en
  AIMA-Python (https://github.com/aimacode/aima-python/blob/master/aima/search.py).
  Los algoritmos de ``campusguard.busquedas`` solo conocen esta interfaz, así
  que funcionan con cualquier problema que la implemente.
* ``CampusGuard`` es el problema concreto: planificar las intervenciones que
  llevan a un estudiante en riesgo de abandono a una situación de riesgo bajo
  con el menor costo posible. Su justificación está en docs/modelo.md.
"""

from __future__ import annotations

from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Representación del estado
# ---------------------------------------------------------------------------

Estado = tuple[int, int, int, int, int]
"""Un estado es una tupla (r, a, c, t, b) de enteros:

* r: nivel de riesgo académico, de 0 a 10.
* a: inasistencias del último mes, de 0 a 8.
* c: nivel de carga académica, de 1 (mínima) a 4 (completa).
* t: tutorías asignadas en el periodo, de 0 a 5.
* b: 1 si ya se notificó a bienestar universitario, 0 si no.

Se usa una tupla porque es inmutable y se puede guardar en conjuntos y como
clave de diccionarios, que es como los algoritmos recuerdan los estados ya
visitados.
"""

# ---------------------------------------------------------------------------
# Acciones y costos
# ---------------------------------------------------------------------------

# Nombres de las acciones. Se definen como constantes para no escribir las
# cadenas a mano en varios lugares y evitar errores de digitación.
TUTORIA = "TUTORIA"            # sesión de tutoría: baja el riesgo en 1
SEGUIMIENTO = "SEGUIMIENTO"    # contacto del docente: baja las inasistencias en 1
ASESORIA = "ASESORIA"          # consejería académica: baja riesgo e inasistencias en 1
BIENESTAR = "BIENESTAR"        # notificar a bienestar: baja el riesgo en 2 y las faltas en 3
AJUSTE_CARGA = "AJUSTE_CARGA"  # cancelar o aplazar una materia: baja el riesgo en 3

COSTOS: dict[str, int] = {
    TUTORIA: 1,
    SEGUIMIENTO: 1,
    ASESORIA: 2,
    BIENESTAR: 4,
    AJUSTE_CARGA: 5,
}
"""Costo de cada acción, en unidades relativas.

Representa los recursos institucionales y el impacto sobre el estudiante. Las
acciones de mayor efecto son las menos eficientes por unidad de mejora, de
modo que el agente debe sopesar cuántas acciones usa frente al costo total.
"""

# ---------------------------------------------------------------------------
# Estado inicial, meta y límites del modelo
# ---------------------------------------------------------------------------

ESTADO_INICIAL: Estado = (10, 8, 4, 0, 0)
"""Estudiante con riesgo máximo, 8 inasistencias, carga completa y sin intervenciones."""

RIESGO_META = 2
"""La meta exige un riesgo menor o igual a este valor (riesgo bajo)."""

INASISTENCIAS_META = 1
"""La meta exige como máximo esta cantidad de inasistencias (asistencia regular)."""

MAX_TUTORIAS = 5
"""Tope de tutorías por periodo; evita que todo se resuelva con la acción más barata."""

CARGA_MINIMA = 1
"""Nivel de carga por debajo del cual ya no se pueden cancelar más materias."""


class Problem:
    """Problema de búsqueda abstracto, con la interfaz de AIMA-Python.

    Las subclases deben definir ``actions`` y ``result``, y pueden redefinir
    ``goal_test``, ``path_cost`` y ``h``. Los algoritmos de búsqueda solo usan
    estos métodos, sin saber nada del problema concreto.
    """

    def __init__(self, initial, goal=None):
        """Guarda el estado inicial y, si el problema tiene una sola meta, ese estado."""
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        """Devuelve la lista de acciones aplicables en ``state``."""
        raise NotImplementedError

    def result(self, state, action):
        """Modelo de transición: el estado que resulta de aplicar ``action`` en ``state``."""
        raise NotImplementedError

    def goal_test(self, state) -> bool:
        """Indica si ``state`` es un estado meta. Por defecto, si es igual a ``goal``."""
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Devuelve el costo de llegar a ``state2`` desde ``state1`` con ``action``.

        ``c`` es el costo acumulado hasta ``state1``. Por defecto cada acción
        cuesta 1, de modo que el costo es igual al número de acciones.
        """
        return c + 1

    def h(self, node) -> float:
        """Heurística: estimación del costo que falta desde ``node`` hasta la meta.

        Por defecto devuelve 0, que equivale a no tener ninguna estimación.
        """
        return 0


class CampusGuard(Problem):
    """Plan de intervenciones para llevar a un estudiante a riesgo bajo.

    Recibe el estado inicial (por defecto ``ESTADO_INICIAL``) y, opcionalmente,
    la heurística que usará A*, como una función que recibe un nodo y devuelve
    un número. Las heurísticas disponibles están en ``campusguard.heuristicas``.
    """

    def __init__(
        self,
        initial: Estado = ESTADO_INICIAL,
        heuristica: Optional[Callable] = None,
    ):
        # Se valida al crear el problema para que un estado mal escrito falle
        # aquí, con un mensaje claro, y no en medio de una búsqueda.
        _validar_estado(initial)
        # No hay un único estado meta (la meta es una condición), así que
        # ``goal`` queda vacío y se redefine ``goal_test``.
        super().__init__(initial)
        self.heuristica = heuristica

    def actions(self, state: Estado) -> list[str]:
        """Devuelve las acciones aplicables en ``state``, según sus condiciones.

        Sobre el orden de la lista: es una convención arbitraria. El modelo no
        dice que una acción deba probarse antes que otra; este es el orden en
        que se escribieron las condiciones y se mantiene fijo para que los
        resultados sean reproducibles.

        El orden no cambia lo que cada algoritmo garantiza, pero sí cómo
        desempata entre soluciones equivalentes. Con los 120 órdenes posibles
        de las cinco acciones:

        * BFS siempre encuentra un plan de 6 acciones (el mínimo), pero su
          costo es 16 o 17 según el orden, y expande entre 105 y 178 nodos.
          Con este orden cuesta 17.
        * DFS no garantiza nada: su plan tiene entre 7 y 15 acciones y cuesta
          entre 15 y 24. Con este orden tiene 8 acciones y cuesta 23.
        * A* siempre encuentra el costo óptimo, 14. Lo que cambia es cuántos
          nodos expande antes de confirmarlo (de 133 a 177 con la heurística
          combinada). Este orden da el mínimo, 133.

        ``tests/test_busquedas.py`` verifica estas garantías con todos los órdenes.
        """
        r, a, c, t, b = state
        acciones = []
        # Solo se puede cancelar una materia si queda más de la carga mínima
        # y si todavía hay riesgo que reducir.
        if c > CARGA_MINIMA and r > 0:
            acciones.append(AJUSTE_CARGA)
        # Bienestar se notifica una sola vez por estudiante.
        if b == 0:
            acciones.append(BIENESTAR)
        # La asesoría actúa sobre ambos problemas, así que necesita los dos.
        if r > 0 and a > 0:
            acciones.append(ASESORIA)
        # Las tutorías tienen un tope por periodo.
        if t < MAX_TUTORIAS and r > 0:
            acciones.append(TUTORIA)
        # El seguimiento del docente solo tiene sentido si hay faltas.
        if a > 0:
            acciones.append(SEGUIMIENTO)
        return acciones

    def result(self, state: Estado, action: str) -> Estado:
        """Aplica ``action`` sobre ``state`` y devuelve el nuevo estado.

        Como las tuplas son inmutables, se construye una tupla nueva en lugar
        de modificar la original. Lanza ``ValueError`` si la acción no es
        aplicable en ese estado, para que un error de modelado no pase en
        silencio.
        """
        if action not in self.actions(state):
            raise ValueError(f"La acción {action} no es aplicable en {state}")
        r, a, c, t, b = state
        if action == TUTORIA:
            return (r - 1, a, c, t + 1, b)
        if action == SEGUIMIENTO:
            return (r, a - 1, c, t, b)
        if action == ASESORIA:
            return (r - 1, a - 1, c, t, b)
        # BIENESTAR y AJUSTE_CARGA pueden bajar un valor más de lo que queda,
        # por eso se recortan con max(..., 0): ningún valor baja de cero.
        if action == BIENESTAR:
            return (max(r - 2, 0), max(a - 3, 0), c, t, 1)
        return (max(r - 3, 0), a, c - 1, t, b)  # AJUSTE_CARGA

    def goal_test(self, state: Estado) -> bool:
        """La meta se cumple con riesgo bajo y asistencia regular.

        Solo importan r y a: la carga, las tutorías y bienestar pueden tener
        cualquier valor al final. Por eso cada algoritmo puede terminar en un
        estado final distinto.
        """
        r, a, _, _, _ = state
        return r <= RIESGO_META and a <= INASISTENCIAS_META

    def path_cost(self, c, state1, action, state2):
        """Suma al costo acumulado ``c`` el costo de ``action`` según ``COSTOS``."""
        return c + COSTOS[action]

    def h(self, node) -> float:
        """Evalúa la heurística configurada en el constructor, o devuelve 0 si no hay."""
        return self.heuristica(node) if self.heuristica else 0


def _validar_estado(state) -> None:
    """Verifica que ``state`` sea una tupla de cinco enteros dentro de su rango.

    Lanza ``ValueError`` indicando qué componente está fuera de rango.
    """
    if not isinstance(state, tuple) or len(state) != 5:
        raise ValueError(f"El estado debe ser una tupla (r, a, c, t, b): {state}")
    r, a, c, t, b = state
    # (valor, mínimo, máximo, nombre) de cada componente del estado.
    rangos = [
        (r, 0, 10, "r"),
        (a, 0, 8, "a"),
        (c, CARGA_MINIMA, 4, "c"),
        (t, 0, MAX_TUTORIAS, "t"),
        (b, 0, 1, "b"),
    ]
    for valor, minimo, maximo, nombre in rangos:
        if not isinstance(valor, int) or not minimo <= valor <= maximo:
            raise ValueError(f"{nombre}={valor} fuera de rango [{minimo}, {maximo}]")
