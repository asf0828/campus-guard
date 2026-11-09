"""Compara BFS, DFS y A* sobre el mismo estado inicial de CampusGuard.

Para cada algoritmo reporta las acciones del plan, su costo, si es óptimo,
los nodos expandidos, el máximo de estados en memoria y el tiempo promedio de
ejecución. A* se ejecuta con cada heurística de ``campusguard.heuristicas``.
Con ``--aima`` agrega las mismas búsquedas ejecutadas con AIMA-Python, para
validar la implementación propia.

Uso:
    python benchmark.py
    python benchmark.py --repeticiones 500 --planes
    python benchmark.py --inicial 8 6 3 0 0 --formato csv
    python benchmark.py --aima
"""

from __future__ import annotations

import argparse
import csv
import sys
import timeit
from dataclasses import dataclass
from typing import Callable

from campusguard.busquedas import (
    Resultado,
    busqueda_a_estrella,
    busqueda_anchura,
    busqueda_profundidad,
)
from campusguard.heuristicas import h_combinada, h_maxima, h_nula
from campusguard.problema import ESTADO_INICIAL, CampusGuard
from campusguard import validacion_aima

ALGORITMOS: list[tuple[str, Callable[[CampusGuard], Resultado]]] = [
    ("BFS", busqueda_anchura),
    ("DFS", busqueda_profundidad),
    ("A* (h nula)", lambda p: busqueda_a_estrella(p, h=h_nula)),
    ("A* (h máxima)", lambda p: busqueda_a_estrella(p, h=h_maxima)),
    ("A* (h combinada)", lambda p: busqueda_a_estrella(p, h=h_combinada)),
]
"""Algoritmos que se comparan, como pares (nombre en la tabla, función).

Cada función recibe el problema y devuelve un ``Resultado``. Las de A* se
envuelven en ``lambda`` para fijar la heurística, de modo que todas tengan la
misma forma y el benchmark las pueda ejecutar igual.
"""

ALGORITMOS_AIMA: list[tuple[str, Callable[[CampusGuard], Resultado]]] = [
    ("BFS (AIMA)", validacion_aima.anchura_aima),
    ("DFS (AIMA)", validacion_aima.profundidad_aima),
    ("A* (AIMA, h nula)", lambda p: validacion_aima.a_estrella_aima(p, h=h_nula)),
    ("A* (AIMA, h máxima)", lambda p: validacion_aima.a_estrella_aima(p, h=h_maxima)),
    ("A* (AIMA, h combinada)",
     lambda p: validacion_aima.a_estrella_aima(p, h=h_combinada)),
]
"""Las mismas búsquedas ejecutadas con AIMA-Python, para validar las propias.

Solo se ejecutan con ``--aima``. Si la implementación propia es correcta, BFS
y A* deben dar los mismos planes, costos y nodos expandidos que estas.
"""

COLUMNAS = [
    "Algoritmo",
    "Acciones",
    "Costo",
    "Óptimo",
    "Nodos expandidos",
    "Estados en memoria (máx.)",
    "Tiempo (ms)",
]
"""Encabezados de la tabla, en el mismo orden en que ``_valores`` arma cada fila."""


@dataclass
class Fila:
    """Una fila de la tabla: el resultado de un algoritmo y su tiempo.

    * ``nombre``: el nombre que aparece en la tabla.
    * ``resultado``: el ``Resultado`` de la búsqueda (plan, costo, métricas).
    * ``tiempo_ms``: tiempo promedio por ejecución, en milisegundos.
    * ``optimo``: si el costo del plan es igual al costo óptimo.
    """

    nombre: str
    resultado: Resultado
    tiempo_ms: float
    optimo: bool


def medir_tiempo(funcion: Callable[[], object], repeticiones: int) -> float:
    """Devuelve el tiempo promedio por ejecución de ``funcion``, en milisegundos.

    Una búsqueda tarda menos de un milisegundo, así que medir una sola
    ejecución daría un número dominado por el ruido. Por eso se ejecuta
    ``repeticiones`` veces seguidas en cinco rondas y se toma la ronda más
    rápida, que es la menos afectada por otros procesos del sistema.
    """
    rondas = timeit.repeat(funcion, number=repeticiones, repeat=5)
    return min(rondas) / repeticiones * 1000


def ejecutar(estado_inicial=ESTADO_INICIAL, repeticiones: int = 100,
             incluir_aima: bool = False) -> list[Fila]:
    """Ejecuta todos los algoritmos sobre el mismo estado inicial y devuelve sus filas.

    Con ``incluir_aima`` agrega las búsquedas de AIMA-Python; lanza
    ``ImportError`` si AIMA no está instalado.
    """
    if incluir_aima and not validacion_aima.aima_disponible():
        raise ImportError(validacion_aima.INSTALACION)
    problema = CampusGuard(estado_inicial)
    # El costo óptimo de referencia se obtiene con A* sin heurística (búsqueda
    # de costo uniforme), que siempre encuentra el plan más barato.
    costo_optimo = busqueda_a_estrella(problema, h=h_nula).costo
    # Primero los algoritmos propios y, si se pide, después los de AIMA.
    algoritmos = ALGORITMOS + (ALGORITMOS_AIMA if incluir_aima else [])
    filas = []
    for nombre, buscar in algoritmos:
        resultado = buscar(problema)  # una ejecución para obtener el plan y las métricas
        tiempo = medir_tiempo(lambda: buscar(problema), repeticiones)  # y muchas para el tiempo
        optimo = resultado.encontrado and resultado.costo == costo_optimo
        filas.append(Fila(nombre, resultado, tiempo, optimo))
    return filas


def _valores(fila: Fila) -> list[str]:
    """Convierte una fila en la lista de textos de cada columna, en el orden de ``COLUMNAS``."""
    r = fila.resultado
    # AIMA no mide la memoria; en ese caso se muestra un guion.
    memoria = "-" if r.max_estados_en_memoria is None else str(r.max_estados_en_memoria)
    if not r.encontrado:
        # Sin solución no hay plan ni costo; se muestran guiones.
        return [fila.nombre, "-", "-", "-", str(r.nodos_expandidos),
                memoria, f"{fila.tiempo_ms:.3f}"]
    return [
        fila.nombre,
        str(len(r.acciones)),
        str(r.costo),
        "Sí" if fila.optimo else "No",
        str(r.nodos_expandidos),
        memoria,
        f"{fila.tiempo_ms:.3f}",
    ]


def tabla_markdown(filas: list[Fila]) -> str:
    """Construye la tabla comparativa en formato Markdown, lista para pegar en un documento."""
    lineas = [
        "| " + " | ".join(COLUMNAS) + " |",
        "|" + "|".join("---" for _ in COLUMNAS) + "|",  # línea que separa el encabezado
    ]
    lineas += ["| " + " | ".join(_valores(f)) + " |" for f in filas]
    return "\n".join(lineas)


def escribir_csv(filas: list[Fila], salida=None) -> None:
    """Escribe la tabla comparativa en formato CSV, para abrirla en una hoja de cálculo.

    ``salida`` es el archivo donde se escribe; por defecto, la pantalla. Se
    resuelve al llamar la función (y no como valor por defecto del
    parámetro) para respetar cualquier redirección de la salida estándar.
    """
    escritor = csv.writer(salida or sys.stdout)
    escritor.writerow(COLUMNAS)
    for fila in filas:
        escritor.writerow(_valores(fila))


def planes(filas: list[Fila]) -> str:
    """Lista el plan de acciones que encontró cada algoritmo."""
    lineas = []
    for fila in filas:
        acciones = fila.resultado.acciones
        lineas.append(f"{fila.nombre}: " + (" → ".join(acciones) if acciones else "-"))
    return "\n".join(lineas)


def main(argumentos=None) -> int:
    """Punto de entrada de la línea de comandos.

    ``argumentos`` permite pasar las opciones como lista desde las pruebas; si
    es ``None``, se leen de la línea de comandos. Devuelve 0 si todo salió bien.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--inicial", nargs=5, type=int, metavar=("R", "A", "C", "T", "B"),
                        default=list(ESTADO_INICIAL),
                        help="estado inicial (por defecto: %(default)s)")
    parser.add_argument("--repeticiones", type=int, default=100,
                        help="ejecuciones por ronda para medir el tiempo (por defecto: 100)")
    parser.add_argument("--formato", choices=["tabla", "csv"], default="tabla",
                        help="formato de salida (por defecto: tabla Markdown)")
    parser.add_argument("--planes", action="store_true",
                        help="muestra el plan de acciones de cada algoritmo")
    parser.add_argument("--aima", action="store_true",
                        help="agrega las búsquedas de AIMA-Python para validar la implementación")
    args = parser.parse_args(argumentos)

    if args.repeticiones < 1:
        parser.error("--repeticiones debe ser al menos 1")
    estado = tuple(args.inicial)
    try:
        filas = ejecutar(estado, args.repeticiones, incluir_aima=args.aima)
    except (ValueError, ImportError) as error:
        # Estado inicial fuera de rango o AIMA no instalado: se muestra como
        # error de uso, con su explicación, y no como un error interno.
        parser.error(str(error))

    if args.formato == "csv":
        escribir_csv(filas)
    else:
        print(f"Estado inicial: {estado}\n")
        print(tabla_markdown(filas))
    if args.planes:
        print("\n" + planes(filas))
    return 0


if __name__ == "__main__":
    # Solo se ejecuta al correr ``python benchmark.py``, no al importarlo.
    sys.exit(main())
