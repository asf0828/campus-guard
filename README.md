# CampusGuard: búsqueda en espacio de estados

CampusGuard es un agente que planifica la secuencia de intervenciones de acompañamiento (tutorías, seguimiento docente, asesoría, bienestar y ajuste de carga) para llevar a un estudiante en riesgo de abandono a una situación de riesgo bajo, con el menor costo institucional posible. En este repositorio se implementan y comparan tres algoritmos de búsqueda sobre el mismo problema: BFS, DFS y A*.

## Modelo del problema

El entorno se abstrae como determinista, discreto, estático y completamente observable en el momento de planificar: el agente trabaja sobre una fotografía de los registros del estudiante, asume que cada intervención produce su efecto esperado y expresa el riesgo en niveles enteros. Si llegan datos nuevos, se vuelve a planificar desde el estado actualizado.

### Estado

Cada estudiante se representa con la tupla `(r, a, c, t, b)`:

| Variable | Significado | Rango |
|---|---|---|
| `r` | Nivel de riesgo académico | 0 a 10 |
| `a` | Inasistencias del último mes | 0 a 8 |
| `c` | Nivel de carga académica (4 = completa) | 1 a 4 |
| `t` | Tutorías asignadas en el periodo | 0 a 5 |
| `b` | Bienestar ya notificado | 0 o 1 |

**Estado inicial:** `(10, 8, 4, 0, 0)`

**Meta:** `r <= 2` y `a <= 1`

### Acciones

| Acción | Condición | Efecto | Costo |
|---|---|---|---|
| `TUTORIA` | `r > 0` y `t < 5` | `r - 1`, `t + 1` | 1 |
| `SEGUIMIENTO` | `a > 0` | `a - 1` | 1 |
| `ASESORIA` | `r > 0` y `a > 0` | `r - 1`, `a - 1` | 2 |
| `BIENESTAR` | `b == 0` | `r - 2`, `a - 3`, `b = 1` | 4 |
| `AJUSTE_CARGA` | `c > 1` y `r > 0` | `r - 3`, `c - 1` | 5 |

Ningún valor baja de 0. El costo de un plan es la suma de los costos de sus acciones.

### Interfaz común

Todo el código usa la misma interfaz, al estilo de AIMA-Python, para que los tres algoritmos trabajen sobre el mismo problema:

- `actions(state)`: lista de acciones aplicables en el estado.
- `result(state, action)`: estado resultante (modelo de transición).
- `goal_test(state)`: `True` si el estado cumple la meta.
- `path_cost(c, state1, action, state2)`: costo acumulado.
- `h(node)`: heurística (solo para A*).

Para el benchmark, un nodo expandido es un nodo al que se le generan sus sucesores. Los tres algoritmos deben contar igual.

## Documentación

La justificación del modelo y de la abstracción del entorno está en [docs/modelo.md](docs/modelo.md). Las convenciones para contribuir al código y a la documentación están en [AGENTS.md](AGENTS.md).

## Referencias

Russell, S., & Norvig, P. (2021). *Artificial intelligence: A modern approach* (4th ed.). Pearson.

AIMA-Python. (s. f.). *Python implementation of algorithms from Russell and Norvig's "Artificial Intelligence: A Modern Approach"*. GitHub. https://github.com/aimacode/aima-python
