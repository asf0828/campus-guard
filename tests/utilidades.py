"""Funciones auxiliares compartidas por las pruebas."""

from campusguard.problema import CampusGuard


def estados_alcanzables(problema: CampusGuard) -> set:
    """Devuelve todos los estados alcanzables desde el estado inicial.

    Es un recorrido simple del grafo de estados: se parte del estado inicial,
    se aplican todas las acciones posibles y se repite con cada estado nuevo
    hasta que no aparecen más. No busca ninguna meta; sirve para revisar
    propiedades de todo el espacio, como su tamaño o la admisibilidad de las
    heurísticas en cada estado.
    """
    alcanzados = {problema.initial}   # estados ya descubiertos
    pendientes = [problema.initial]   # estados descubiertos que falta recorrer
    while pendientes:
        estado = pendientes.pop()
        for accion in problema.actions(estado):
            siguiente = problema.result(estado, accion)
            if siguiente not in alcanzados:
                alcanzados.add(siguiente)
                pendientes.append(siguiente)
    return alcanzados
