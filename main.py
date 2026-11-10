
from campus_guard import CampusGuard, BIENESTAR, CARGA, ASESORIA, TUTORIA


def main():
    problem = CampusGuard()
    initial_state = problem.get_initial_state()

    print("==================================================")
    print(" VERIFICACIÓN DEL ENTORNO CAMPUSGUARD")
    print("==================================================")
    print(f"Estado Inicial (r, a, c, t, b): {initial_state}")
    print(f"¿Es Meta Inicialmente?: {problem.goal_test(initial_state)}")
    print(f"Acciones Posibles: {problem.actions(initial_state)}")
    print(f"Valor Heurístico h(s0): {problem.h(initial_state)}")

    # Simulación paso a paso de prueba
    pasos = [BIENESTAR, CARGA, ASESORIA, TUTORIA, ASESORIA]
    estado_actual = initial_state
    costo_total = 0.0

    print("\n--- EJECUCIÓN DE SECUENCIA DE PRUEBA ---")
    for i, accion in enumerate(pasos, start=1):
        nuevo_estado = problem.result(estado_actual, accion)
        costo_total = problem.path_cost(costo_total, estado_actual, accion, nuevo_estado)
        print(f"Paso {i}: {accion:12s} | Nuevo Estado: {nuevo_estado} | Costo Acumulado: {costo_total}")
        estado_actual = nuevo_estado

    print("\n--- EVALUACIÓN FINAL ---")
    print(f"Estado Alcanzado: {estado_actual}")
    print(f"¿Meta Lograda (r <= 2, a <= 1)?: {problem.goal_test(estado_actual)}")


if __name__ == "__main__":
    main()