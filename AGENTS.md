# AGENTS.md

Guía para cualquier persona o agente de IA que trabaje en este repositorio. Léela antes de escribir código o documentación.

## Qué es este proyecto

CampusGuard planifica la secuencia de intervenciones que lleva a un estudiante en riesgo de abandono a una situación de riesgo bajo con el menor costo posible. El problema se modela como búsqueda en un espacio de estados y se resuelve con BFS, DFS y A*, que luego se comparan entre sí. El modelo completo está en `README.md` y su justificación en `docs/modelo.md`.

## El modelo es un contrato

Todo el código depende de la misma definición del problema. No cambies el estado, las acciones, sus condiciones, sus efectos, sus costos, el estado inicial ni la meta sin acordarlo antes con el equipo. Si un cambio se aprueba, actualiza en el mismo commit `README.md`, `docs/modelo.md` y el código.

Las reglas que no se deben romper:

- El estado es una tupla inmutable `(r, a, c, t, b)` de enteros. No uses listas, diccionarios ni clases para representarlo, porque los algoritmos lo guardan en conjuntos y diccionarios.
- Las acciones se identifican con estas cadenas exactas: `TUTORIA`, `SEGUIMIENTO`, `ASESORIA`, `BIENESTAR`, `AJUSTE_CARGA`.
- Ningún componente del estado baja de 0. Los efectos se recortan con `max(valor, 0)`.
- Toda acción reduce `r`, `a` o `c`, o cambia `b` de 0 a 1. Por eso el espacio no tiene ciclos y todo camino es finito. Si una acción nueva rompe esta propiedad, DFS deja de tener garantías y hay que discutirlo.
- Desde el estado inicial `(10, 8, 4, 0, 0)` se alcanzan 935 estados, el costo óptimo es 14 y la solución menos profunda tiene 6 acciones. Si tus cambios alteran estas cifras, algo se rompió en el modelo.

## Organización del código

Al crear archivos, usa esta organización:

| Ruta | Contenido |
|---|---|
| `campusguard/problema.py` | Clase del problema CampusGuard |
| `campusguard/busquedas.py` | BFS, DFS y A*, independientes del problema |
| `campusguard/heuristicas.py` | Funciones heurísticas para A* |
| `campusguard/validacion_aima.py` | Búsquedas de AIMA-Python para validar las propias |
| `benchmark.py` | Ejecuta los tres algoritmos y genera la tabla comparativa |
| `tests/` | Pruebas con `unittest`, una por módulo (`test_<modulo>.py`) |
| `docs/` | Documentación del proyecto en Markdown |
| `requirements.txt` | Dependencias, si llega a haber alguna |

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

Los algoritmos reciben un problema y devuelven el camino encontrado, su costo y las métricas. No deben conocer los detalles de CampusGuard: si un algoritmo menciona `r` o `TUTORIA`, está acoplado al problema y hay que corregirlo.

## Métricas del benchmark

Los tres algoritmos se miden con los mismos criterios, o la comparación no vale:

- **Nodo expandido:** nodo al que se le generan sus sucesores. Se cuenta igual en BFS, DFS y A*.
- **Tiempo:** promedio de muchas ejecuciones con `timeit`, porque una sola corrida dura menos de un milisegundo.
- **Costo:** suma de los costos de las acciones del plan.
- Siempre el mismo estado inicial y la misma meta.

Las heurísticas viven en `campusguard/heuristicas.py`. Toda heurística nueva debe probarse admisible y consistente recorriendo los estados alcanzables (`h(n) <= h*(n)` y `h(n) <= costo(n, n') + h(n')`) antes de usarse en resultados.

## Convenciones de código

- Python 3.10 o superior, solo biblioteca estándar salvo que el equipo acuerde otra cosa. Si se agrega una dependencia, va en `requirements.txt`.
- AIMA-Python es la única excepción: es opcional, se usa solo en `campusguard/validacion_aima.py` y sus pruebas, y se instala fijada a un commit como explica el README. Ningún otro módulo debe importarla, y todo debe seguir funcionando sin ella.
- Si cambias una búsqueda propia, corre también las pruebas con AIMA instalado: BFS y A* deben seguir coincidiendo con AIMA en plan, costo y nodos expandidos.
- Nombres de módulos, funciones y variables en español y en `snake_case`, sin tildes ni ñ en los identificadores.
- Cada función, clase, constante y diccionario lleva un docstring o comentario que diga qué es o qué hace, qué recibe y qué devuelve.
- El código debe servir también para entender los algoritmos. Explica con comentarios los pasos que no son obvios para alguien que está aprendiendo búsqueda: por qué se usa una cola o una pila, cuándo se prueba la meta y por qué, qué significa cada métrica, por qué una heurística es admisible. Comenta el porqué y no repitas lo que la línea ya dice.
- Si adaptas código de AIMA-Python, indícalo en el docstring del módulo con el enlace al archivo original.
- Antes de hacer commit, ejecuta `python -m unittest` y `python benchmark.py`. Las pruebas verifican las cifras de control del modelo y la admisibilidad de las heurísticas; si alguna falla, no subas el cambio.
- Todo comportamiento nuevo lleva su prueba en `tests/`.

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
