# AGENTS.md

Guía para cualquier persona o agente de IA que trabaje en este repositorio. Léela antes de escribir código o documentación.

## Qué es este proyecto

CampusGuard planifica la secuencia de intervenciones que lleva a un estudiante en riesgo de abandono a una situación de riesgo bajo con el menor costo posible. El problema se modela como búsqueda en un espacio de estados y se resuelve con BFS, DFS y A*, que luego se comparan entre sí. El modelo completo está en `README.md`, su justificación en `docs/modelo.md` y el análisis de complejidad en `docs/big-o-analysis.md`.

## El modelo es un contrato

Todo el código depende de la misma definición del problema. No cambies el estado, las acciones, sus condiciones, sus efectos, sus costos, el estado inicial ni la meta sin acordarlo antes con el equipo. Si un cambio se aprueba, actualiza en el mismo commit `README.md`, `docs/modelo.md` y el código.

Las reglas que no se deben romper:

- El estado es una tupla inmutable `(r, a, c, t, b)` de enteros. No uses listas, diccionarios ni clases para representarlo, porque los algoritmos lo guardan en conjuntos y diccionarios.
- Las acciones se identifican con estas cadenas exactas: `TUTORIA`, `SEGUIMIENTO`, `ASESORIA`, `BIENESTAR`, `AJUSTE_CARGA`.
- Ningún componente del estado baja de 0. Los efectos se recortan con `max(valor, 0)`.
- Toda acción reduce `r`, `a` o `c`, o cambia `b` de 0 a 1. Por eso el espacio no tiene ciclos y todo camino es finito. Si una acción nueva rompe esta propiedad, DFS deja de tener garantías y hay que discutirlo.
- Desde el estado inicial `(10, 8, 4, 0, 0)` se alcanzan 935 estados, el costo óptimo es 14 y la solución menos profunda tiene 6 acciones. Si tus cambios alteran estas cifras, algo se rompió en el modelo.

## Organización del código

Cada concepto vive en un solo archivo. Antes de definir algo, revisa si ya existe e impórtalo en lugar de copiarlo.

| Archivo | Contenido |
|---|---|
| `problema.py` | `ProblemaCampusGuard` y `Nodo`, la base común que importan las búsquedas |
| `heuristicas.py` | La heurística de A*; el problema la expone en su método `h` |
| `busqueda_no_informada.py` | BFS y DFS |
| `busqueda_informada.py` | A* |
| `benchmark.py` | Importa los tres algoritmos y los compara; no define algoritmos propios |
| `docs/` | Documentación del proyecto en Markdown |

Si cambias la forma de ejecutar el proyecto, actualiza la sección "Cómo ejecutar" del `README.md`.

## Interfaz común

La clase del problema sigue la interfaz de AIMA-Python, para que cualquier algoritmo funcione sobre ella sin adaptaciones:

```python
actions(state) -> list[str]
result(state, action) -> tuple
goal_test(state) -> bool
path_cost(c, state1, action, state2) -> float
h(node) -> float   # solo para A*
```

Los algoritmos reciben un problema y devuelven el camino encontrado, su costo y las métricas. No deben conocer los detalles de CampusGuard: si un algoritmo menciona `r` o `TUTORIA`, está acoplado al problema y hay que corregirlo. Por eso A* obtiene la heurística con `problema.h(nodo)` y no llamando directamente a la función de `heuristicas.py`.

## Métricas del benchmark

Los tres algoritmos se miden con los mismos criterios, o la comparación no vale:

- **Nodo expandido:** nodo al que se le generan sus sucesores. Se cuenta igual en BFS, DFS y A*.
- **Tiempo:** promedio de muchas ejecuciones con `timeit`, porque una sola corrida dura menos de un milisegundo.
- **Costo:** suma de los costos de las acciones del plan, en unidades relativas (no son horas).
- Siempre el mismo estado inicial y la misma meta.

Las heurísticas viven en `heuristicas.py`. Toda heurística nueva debe probarse admisible y consistente recorriendo los estados alcanzables (`h(n) <= h*(n)` y `h(n) <= costo(n, n') + h(n')`) antes de usarse en resultados.

## Convenciones de código

- Python 3.10 o superior, solo biblioteca estándar salvo que el equipo acuerde otra cosa. Si se agrega una dependencia, crea un `requirements.txt` con ella y explícalo en el README.
- Nombres de módulos, funciones y variables en español y en `snake_case`, sin tildes ni ñ en los identificadores.
- Cada función pública lleva un docstring corto que diga qué hace, qué recibe y qué devuelve.
- Si adaptas código de AIMA-Python, indícalo en el docstring del módulo con el enlace al archivo original.
- Antes de hacer commit, ejecuta `python benchmark.py` y verifica que los tres algoritmos sigan encontrando una solución válida con las cifras de la tabla del README: BFS 175 nodos y costo 16, DFS 8 y 23, A* 136 y 14. Si cambian, algo se rompió.

## Documentación

La documentación del proyecto vive en `docs/`, en Markdown. Al escribirla:

- Redacta en párrafos de corrido. Usa tablas cuando ayuden y listas solo para enumeraciones cortas.
- Usa títulos con nombre propio, sin numeración (nada de `1.`, `2.1`).
- No pongas líneas divisorias entre secciones.
- Escribe sobre el proyecto en sí. No menciones cursos, materias, entregas, fechas límite, universidades ni personas.
- Cita las fuentes en formato APA 7 y agrégalas a la sección de referencias del archivo.

## Git

- Trabaja con commits pequeños y mensajes en español que digan qué cambió.
- Nunca hagas `push --force` sobre `main`. Si algo salió mal, corrígelo con un commit nuevo.
- Antes de hacer push, ejecuta `git pull --rebase` para integrar lo que hayan subido los demás.
