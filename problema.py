
"""Modelo del problema CampusGuard."""


class ProblemaCampusGuard:
    """Problema de planificacion de intervenciones para un estudiante en riesgo.

    Estado: tupla (r, a, c, t, b)
        r: nivel de riesgo academico (0 a 10)
        a: inasistencias recientes (0 a 8)
        c: nivel de carga academica (1 a 4)
        t: tutorias asignadas (0 a 5)
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
        """Recibe el estado inicial del problema."""
        self.initial = initial

    def actions(self, state):
        """Devuelve las acciones aplicables en el estado actual."""
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
        """Devuelve el estado resultante de aplicar una accion."""
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

        raise ValueError(f'Accion desconocida: {action}')

    def goal_test(self, state):
        """Comprueba si el estudiante alcanzo la meta."""
        r, a, _, _, _ = state
        return r <= 2 and a <= 1

    def path_cost(self, c, state1, action, state2):
        """Devuelve el costo acumulado de las acciones."""
        return c + self.COSTOS[action]
