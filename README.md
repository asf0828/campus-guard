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

## Cómo ejecutar

Se necesita Python 3.10 o superior. El proyecto solo usa la biblioteca estándar, así que no hay que instalar nada.

```bash
git clone https://github.com/asf0828/campus-guard.git
cd campus-guard
python benchmark.py
```

El benchmark ejecuta BFS, DFS y A* (con tres heurísticas) sobre el mismo estado inicial y muestra una tabla con las acciones del plan, su costo, si es óptimo, los nodos expandidos, el máximo de estados en memoria y el tiempo promedio. Algunas opciones útiles:

```bash
python benchmark.py --planes                  # muestra el plan de cada algoritmo
python benchmark.py --repeticiones 500        # más ejecuciones para medir el tiempo
python benchmark.py --inicial 6 4 2 0 0       # otro estado inicial (r a c t b)
python benchmark.py --formato markdown > resultados.md   # tabla para documentos
python benchmark.py --formato csv > resultados.csv       # para hojas de cálculo
```

Por defecto la tabla sale en texto alineado para leerla en la terminal, y los planes agrupan las acciones repetidas seguidas (`ASESORIA ×4`).

Para usar los algoritmos desde Python:

```python
from campusguard.problema import CampusGuard
from campusguard.busquedas import busqueda_a_estrella
from campusguard.heuristicas import h_combinada

resultado = busqueda_a_estrella(CampusGuard(), h=h_combinada)
print(resultado.acciones, resultado.costo, resultado.nodos_expandidos)
```

### Pruebas

```bash
python -m unittest -v
```

Las pruebas verifican el modelo (935 estados alcanzables, sin ciclos), los resultados de cada algoritmo, que las heurísticas sean admisibles y consistentes en todos los estados alcanzables, y el script de benchmark.

### Validación con AIMA-Python

Los algoritmos propios se pueden comparar con los de [AIMA-Python](https://github.com/aimacode/aima-python), que se aplican directamente sobre `CampusGuard` porque comparte la interfaz de su clase `Problem`. Es una dependencia opcional: sin ella, todo lo anterior funciona igual y las pruebas de validación se omiten.

AIMA-Python no se publica en PyPI y su instalación normal arrastra paquetes de aprendizaje automático que la búsqueda no usa, así que se instala sin dependencias, más NumPy, dentro de un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --no-deps "git+https://github.com/aimacode/aima-python.git@49ebbc316192e84489f8bcb061e24b69150598fc"
pip install numpy
```

pip avisará que a `aima` le faltan dependencias como TensorFlow; para este proyecto no hacen falta. Con el entorno activo:

```bash
python benchmark.py --aima
python -m unittest tests.test_validacion_aima -v
```

BFS y A* (con las tres heurísticas) dan los mismos planes, costos y nodos expandidos en ambas implementaciones. DFS difiere porque AIMA apila los sucesores en el orden en que los devuelve `actions` y explora primero la última acción, mientras que la implementación propia explora primero la primera; eso muestra cuánto depende DFS del orden de las acciones. AIMA no mide los estados en memoria y es más lento, porque comprueba si un nodo está en la frontera recorriéndola completa.

## Código

| Ruta | Contenido |
|---|---|
| `campusguard/problema.py` | Clase base `Problem` y el problema `CampusGuard` |
| `campusguard/busquedas.py` | BFS, DFS y A* en grafo, independientes del problema |
| `campusguard/heuristicas.py` | Heurísticas nula, máxima y combinada para A* |
| `campusguard/validacion_aima.py` | Las mismas búsquedas ejecutadas con AIMA-Python (opcional) |
| `benchmark.py` | Tabla comparativa de los algoritmos |
| `tests/` | Pruebas del modelo, las búsquedas, las heurísticas y el benchmark |

## Documentación

La justificación del modelo y de la abstracción del entorno está en [docs/modelo.md](docs/modelo.md). Las convenciones para contribuir al código y a la documentación están en [AGENTS.md](AGENTS.md).

## Referencias

Russell, S., & Norvig, P. (2021). *Artificial intelligence: A modern approach* (4th ed.). Pearson.

AIMA-Python. (s. f.). *Python implementation of algorithms from Russell and Norvig's "Artificial Intelligence: A Modern Approach"*. GitHub. https://github.com/aimacode/aima-python
