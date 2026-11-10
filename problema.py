
class ProblemaCampusGuard:

    inicial = (10, 8, 4, 0, 0)

    costos = {
        "TUTORIA": 1,
        "SEGUIMIENTO": 1,
        "ASESORIA": 2,
        "BIENESTAR": 4,
        "AJUSTE_CARGA": 5,
    }

    def __init__(self, initial=None):
        self.initial = self.inicial if initial is None else tuple(initial)

    def actions(self, state):
        r, a, c, t, b = state
        acciones = []

        if r > 0 and t < 5:
            acciones.append("TUTORIA")
        if a > 0:
            acciones.append("SEGUIMIENTO")
        if r > 0 and a > 0:
            acciones.append("ASESORIA")
        if b == 0:
            acciones.append("BIENESTAR")
        if c > 1 and r > 0:
            acciones.append("AJUSTE_CARGA")

        return acciones

    def result(self, state, action):
        r, a, c, t, b = state

        if action == "TUTORIA":
            return (max(0, r - 1), a, c, t + 1, b)
        if action == "SEGUIMIENTO":
            return (r, max(0, a - 1), c, t, b)
        if action == "ASESORIA":
            return (max(0, r - 1), max(0, a - 1), c, t, b)
        if action == "BIENESTAR":
            return (max(0, r - 2), max(0, a - 3), c, t, 1)
        if action == "AJUSTE_CARGA":
            return (max(0, r - 3), a, c - 1, t, b)

        raise ValueError(f"Acción desconocida: {action}")

    def goal_test(self, state):
        r, a, _, _, _ = state
        return r <= 2 and a <= 1

    def path_cost(self, cost_so_far, state1, action, state2):
        return cost_so_far + self.costos[action]
