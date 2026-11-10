# Complejidad algorítmica de las búsquedas

## Propósito

Este documento analiza el costo computacional de las estrategias BFS, DFS y A* implementadas para CampusGuard. La comparación separa la complejidad teórica del comportamiento observado en las ejecuciones: la primera describe cómo puede crecer el trabajo al aumentar el espacio de búsqueda; el segundo depende del modelo concreto, del orden de las acciones, de la implementación y del equipo donde se ejecuta.

## Parámetros del espacio de búsqueda

CampusGuard representa cada estudiante mediante el estado `(r, a, c, t, b)`. Desde el estado inicial `(10, 8, 4, 0, 0)`, la meta se alcanza cuando `r ≤ 2` y `a ≤ 1`. El modelo documenta 935 estados alcanzables, un factor de ramificación máximo `b = 5`, una profundidad máxima `m = 16` y una solución menos profunda de `d = 6` acciones. El costo óptimo registrado para alcanzar la meta es 14 unidades de costo institucional.

| Símbolo | Significado en el análisis | Valor documentado |
|---|---|---:|
| `b` | Factor de ramificación máximo: mayor número de acciones aplicables desde un estado | 5 |
| `d` | Profundidad de la solución menos profunda | 6 |
| `m` | Profundidad máxima del espacio de búsqueda | 16 |
| `N` | Número de estados alcanzables desde el estado inicial | 935 |
| `b*` | Factor de ramificación efectivo equivalente | No calculado |

El valor `b = 5` es un máximo, no significa que todas las acciones estén disponibles en todos los estados. El modelo reporta un promedio de 3,9 acciones aplicables por estado. Además, `N = 935` corresponde a los estados alcanzables a todas las profundidades, hasta `m = 16`; por ello no debe combinarse directamente con `d = 6` para obtener un `b*` válido.

## Complejidad de BFS

La búsqueda en anchura (BFS) explora los nodos por niveles, comenzando por los estados más cercanos al inicial. En el peor caso, si la solución se encuentra a profundidad `d` y el factor de ramificación es `b`, puede generar una cantidad de nodos proporcional a:

$$
1+b+b^2+\cdots+b^d = O(b^d)
$$

Por tanto, su complejidad temporal es `O(b^d)`. Su complejidad espacial también es `O(b^d)`, porque debe conservar la frontera de búsqueda y los estados alcanzados para evitar repetir exploraciones. BFS encuentra una solución de menor profundidad cuando las acciones se consideran con el mismo costo; esto no garantiza el menor costo acumulado cuando las acciones tienen costos diferentes, como ocurre en CampusGuard.

## Complejidad de DFS

La búsqueda en profundidad (DFS) continúa por una rama hasta que no puede avanzar y después retrocede para explorar alternativas. En un árbol de búsqueda con profundidad máxima `m`, su complejidad temporal es `O(b^m)`. La memoria de la versión clásica en árbol es `O(b · m)`, ya que conserva principalmente la ruta actual y las alternativas pendientes.

En una búsqueda sobre grafo, como la que registra estados explorados para evitar ciclos o repeticiones, el consumo real de memoria también incluye ese conjunto de estados visitados. Por ello, `O(b · m)` describe la cota clásica de DFS en árbol, pero no necesariamente toda la memoria de la implementación de CampusGuard. DFS puede encontrar una solución rápidamente según el orden de las acciones, pero no garantiza que sea la de menor profundidad ni la de menor costo.

## Complejidad de A*

A* prioriza los nodos mediante la función:

$$
f(n)=g(n)+h(n)
$$

`g(n)` representa el costo acumulado desde el estado inicial y `h(n)` estima el costo restante hasta la meta. La heurística permite orientar la exploración hacia estados que parecen prometedores, reduciendo potencialmente el número de expansiones frente a una búsqueda no informada.

Sin embargo, A* no tiene una mejora polinómica garantizada por utilizar una heurística. En el peor caso, su tiempo y su memoria pueden crecer exponencialmente; una cota habitual para el análisis general es `O(b^d)` para ambos recursos. El comportamiento efectivo depende de la calidad de `h(n)`, de la distribución de costos y de la estructura del espacio de estados. La expresión `O(b^(d-k_h))` puede usarse únicamente como intuición simplificada del efecto de una heurística, no como cota general garantizada.

En CampusGuard, la heurística documentada se construye sobre una abstracción del estado y un problema relajado. Para conservar la garantía de optimalidad de A*, debe ser admisible, es decir, no sobreestimar el costo real mínimo restante. La demostración específica de esa propiedad debe mantenerse junto con la documentación de la heurística.

## Comparación de las cotas

| Algoritmo | Tiempo (peor caso) | Espacio (cota clásica) | Criterio de exploración |
|---|---|---|---|
| BFS | `O(b^d)` | `O(b^d)` | Menor profundidad primero |
| DFS | `O(b^m)` | `O(b · m)` en árbol; más el conjunto de visitados en búsqueda sobre grafo | Profundiza por una rama |
| A* | Exponencial; comúnmente `O(b^d)` | Exponencial; comúnmente `O(b^d)` | Menor `g(n) + h(n)` primero |

Estas cotas son análisis generales de los algoritmos. No deben confundirse con el número de estados alcanzables del modelo ni con los tiempos medidos en una ejecución concreta.

## Resultados experimentales disponibles

La tabla siguiente recoge los resultados comparativos registrados para el estado inicial y la meta del modelo. Los costos son unidades relativas de costo institucional definidas por las acciones; no representan horas reales. Los tiempos son mediciones de ejecución y pueden variar entre equipos y corridas.

| Algoritmo | Nodos expandidos | Tiempo registrado | Costo del plan |
|---|---:|---:|---:|
| BFS | 175 | 1,74 ms | 16 |
| DFS | 8 | 0,07 ms | 23 |
| A* | 136 | 2,72 ms | 14 |

En estos resultados, A* expandió 136 nodos frente a los 175 de BFS. La reducción relativa de expansiones fue:

$$
\frac{175-136}{175}\times 100 \approx 22,29\%
$$

A* obtuvo el menor costo registrado (14), mientras que BFS encontró un plan de menor profundidad, pero no de menor costo total. DFS expandió menos nodos en esta ejecución, aunque su plan tuvo un costo mayor (23); por tanto, contar expansiones por sí solo no permite concluir que un algoritmo haya encontrado una mejor solución. El tiempo registrado de A* también fue mayor en esta corrida, lo que muestra que una reducción en expansiones no implica necesariamente un menor tiempo de ejecución: la gestión de prioridades y el cálculo de la heurística tienen un costo adicional.

Estas cifras deben actualizarse si cambia el código o se ejecuta un benchmark nuevo. Para una comparación reproducible, los tres algoritmos deben usar el mismo estado inicial, la misma meta y la misma convención de conteo: un nodo expandido es aquel al que se le generan sus sucesores. El tiempo debe calcularse como promedio de múltiples ejecuciones, tal como establece la guía del repositorio.

## Factor de ramificación efectivo

El factor de ramificación efectivo `b*` es el valor que satisface la ecuación:

$$
N=1+b^*+(b^*)^2+\cdots+(b^*)^d
$$

Su interpretación exige que `N` sea el número de nodos generados hasta la profundidad de solución `d`, usando una convención de conteo uniforme. Aunque el modelo informa 935 estados alcanzables, estos abarcan profundidades hasta `m = 16`, mientras que `d = 6` es la profundidad de la solución menos profunda. Por esa diferencia, y porque los resultados disponibles no incluyen un conteo homogéneo de nodos generados hasta `d` para cada algoritmo, no se reporta un valor numérico de `b*`.

Para calcularlo en una versión posterior del benchmark, se debe registrar el total de nodos generados hasta encontrar la solución, definir si el nodo inicial y el nodo meta se incluyen en `N`, y aplicar exactamente la misma convención a BFS, DFS y A*. Después se resuelve numéricamente la ecuación para `b*`.

## Consideraciones para interpretar los resultados

La complejidad Big O describe el crecimiento asintótico y no predice por sí sola cuál algoritmo será más rápido en una instancia pequeña. En CampusGuard, el espacio alcanzable está acotado y contiene 935 estados; por eso, las mediciones concretas también dependen de las estructuras de datos, del orden de generación de acciones, de la cola de prioridad de A* y del costo de evaluar la heurística.

La comparación debe considerar conjuntamente nodos expandidos, tiempo de ejecución y costo del plan. BFS favorece soluciones de menor profundidad; DFS puede hallar rápidamente una solución que no sea óptima; A* utiliza información heurística para buscar un plan de menor costo y conserva esa garantía cuando su heurística es admisible y la implementación gestiona correctamente los costos y estados alcanzados.

## Referencias

Russell, S., & Norvig, P. (2021). *Artificial intelligence: A modern approach* (4th ed.). Pearson.

AIMA-Python. (s. f.). *Python implementation of algorithms from Russell and Norvig's “Artificial Intelligence: A Modern Approach”*. GitHub. https://github.com/aimacode/aima-python
