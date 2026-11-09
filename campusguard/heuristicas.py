"""Heurísticas para A* en el problema CampusGuard.

Una heurística h(n) estima el costo que falta para llegar desde un estado
hasta la meta. A* la usa para decidir qué nodo explorar primero: cuanto más
se acerque la estimación al costo real, menos nodos necesita expandir.

Para que A* garantice el plan más barato, la heurística debe cumplir dos
propiedades:

* Admisible: nunca sobreestima. h(n) <= h*(n), donde h*(n) es el costo real
  mínimo desde n hasta la meta.
* Consistente: no baja más de lo que cuesta un paso.
  h(n) <= c(n, a, n') + h(n') para todo sucesor n' de n.

Las tres heurísticas de este módulo cumplen ambas. Las pruebas de
``tests/test_heuristicas.py`` lo verifican sobre los 935 estados alcanzables.

Cada heurística recibe un nodo o directamente un estado. Se llama "exceso" a
lo que separa un estado de la meta: los puntos de riesgo por encima de
``RIESGO_META`` y las inasistencias por encima de ``INASISTENCIAS_META``.
"""

from __future__ import annotations

from campusguard.problema import INASISTENCIAS_META, RIESGO_META


def _excesos(nodo_o_estado) -> tuple[int, int, int]:
    """Devuelve (exceso de riesgo, exceso de inasistencias, b) de un nodo o estado.

    Un exceso nunca es negativo: si el riesgo ya está por debajo de la meta,
    su exceso es 0.
    """
    estado = getattr(nodo_o_estado, "estado", nodo_o_estado)
    r, a, _, _, b = estado
    return max(r - RIESGO_META, 0), max(a - INASISTENCIAS_META, 0), b


def h_nula(nodo_o_estado) -> int:
    """Siempre devuelve 0.

    Es admisible de forma trivial, pero no le da ninguna pista a A*, que se
    comporta entonces como búsqueda de costo uniforme. Sirve como línea base
    para medir cuánto ayudan las otras heurísticas.
    """
    return 0


def h_maxima(nodo_o_estado) -> int:
    """Devuelve el mayor de los dos excesos.

    Ninguna acción baja un punto de riesgo o una inasistencia por menos de 1,
    y hay que eliminar por completo el mayor de los dos excesos; por eso nunca
    sobreestima. Se queda corta porque ignora el otro exceso: en el estado
    inicial estima 8 cuando el costo real es 14.
    """
    exceso_riesgo, exceso_inasistencias, _ = _excesos(nodo_o_estado)
    return max(exceso_riesgo, exceso_inasistencias)


def h_combinada(nodo_o_estado) -> int:
    """Suma ambos excesos y resta 1 si BIENESTAR todavía está disponible.

    El razonamiento es por eficiencia de cada acción, medida en puntos de
    exceso eliminados por unidad de costo:

    * TUTORIA (1 punto por costo 1), SEGUIMIENTO (1 por 1) y ASESORIA (2 por 2)
      eliminan exactamente un punto por unidad de costo.
    * AJUSTE_CARGA elimina 3 puntos por costo 5: es menos eficiente.
    * BIENESTAR elimina hasta 5 puntos (2 de riesgo y 3 de faltas) por costo
      4: es la única más eficiente, ahorra como máximo 1 y se usa una vez.

    Entonces el costo real nunca es menor que la suma de los excesos menos ese
    posible ahorro, y la heurística es admisible. En el estado inicial estima
    8 + 7 - 1 = 14, exactamente el costo real.
    """
    exceso_riesgo, exceso_inasistencias, b = _excesos(nodo_o_estado)
    ahorro_bienestar = 1 if b == 0 else 0  # b == 0: bienestar aún no se ha usado
    # max(..., 0) evita valores negativos cuando ya casi se cumple la meta.
    return max(exceso_riesgo + exceso_inasistencias - ahorro_bienestar, 0)


HEURISTICAS = {
    "nula": h_nula,
    "maxima": h_maxima,
    "combinada": h_combinada,
}
"""Heurísticas disponibles, por nombre. Las pruebas recorren este diccionario
para verificar todas a la vez, así que una heurística nueva debe agregarse aquí."""
