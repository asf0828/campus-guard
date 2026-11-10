
from typing import List, Tuple

# Constantes de Acciones
TUTORIA = "TUTORIA"
SEGUIMIENTO = "SEGUIMIENTO"
ASESORIA = "ASESORIA"
BIENESTAR = "BIENESTAR"
CARGA = "CARGA"


class CampusGuard:
    

    def __init__(self, initial_state: Tuple[int, int, int, int, int] = (10, 8, 4, 0, 0)):
        self.initial_state = initial_state

    def get_initial_state(self) -> Tuple[int, int, int, int, int]:
        
        return self.initial_state

    def actions(self, state: Tuple[int, int, int, int, int]) -> List[str]:
    
        r, a, c, t, b = state
        valid_actions = []

        if r > 0 and t < 5:
            valid_actions.append(TUTORIA)
        if a > 0:
            valid_actions.append(SEGUIMIENTO)
        if r > 0 and a > 0:
            valid_actions.append(ASESORIA)
        if b == 0:
            valid_actions.append(BIENESTAR)
        if c > 1 and r > 0:
            valid_actions.append(CARGA)

        return valid_actions

    def result(
        self, state: Tuple[int, int, int, int, int], action: str
    ) -> Tuple[int, int, int, int, int]:
        
        r, a, c, t, b = state

        if action == TUTORIA:
            return (max(0, r - 1), a, c, t + 1, b)
        elif action == SEGUIMIENTO:
            return (r, max(0, a - 1), c, t, b)
        elif action == ASESORIA:
            return (max(0, r - 1), max(0, a - 1), c, t, b)
        elif action == BIENESTAR:
            return (max(0, r - 2), max(0, a - 3), c, t, 1)
        elif action == CARGA:
            return (max(0, r - 3), a, c - 1, t, b)

        raise ValueError(f"Acción no válida: {action}")

    def goal_test(self, state: Tuple[int, int, int, int, int]) -> bool:
    
        r, a, c, t, b = state
        return r <= 2 and a <= 1

    def path_cost(
        self, c_accumulated: float, state1: Tuple[int, int, int, int, int], action: str, state2: Tuple[int, int, int, int, int]
    ) -> float:
   
        return c_accumulated + self.cost(action)

    def cost(self, action: str) -> float:
 
        costs = {
            TUTORIA: 1.0,
            SEGUIMIENTO: 1.0,
            ASESORIA: 2.0,
            BIENESTAR: 4.0,
            CARGA: 5.0,
        }
        return costs.get(action, 1.0)

    def h(self, state: Tuple[int, int, int, int, int]) -> float:
       
        r, a, c, t, b = state
        r_needed = max(0, r - 2)
        a_needed = max(0, a - 1)
        return float(max(r_needed, a_needed))

    # --- ALIAS DE COMPATIBILIDAD ---
    get_actions = actions
    get_successor = result
    is_goal_state = goal_test
    heuristic = h