# Complejidad algorítmica de las búsquedas

## Propósito

Este documento analiza el costo computacional de las estrategias BFS, DFS y A* implementadas para CampusGuard. La comparación distingue entre la complejidad teórica y el comportamiento observado durante las ejecuciones. La primera describe cómo puede crecer el trabajo computacional al aumentar el espacio de búsqueda, mientras que el segundo depende del modelo concreto, del orden de las acciones, de la implementación y del equipo donde se ejecuta.

## Parámetros del espacio de búsqueda

CampusGuard representa cada estudiante mediante el estado `(r, a, c, t, b)`. Desde el estado inicial `(10, 8, 4, 0, 0)`, se alcanza la meta cuando $r \leq 2$ y $a \leq 1$.

El modelo documenta 935 estados alcanzables, un factor de ramificación máximo $b = 5$, una profundidad máxima $m = 16$ y una solución de menor profundidad de $d = 6$ acciones. El costo óptimo registrado para alcanzar la meta es de 14 unidades de costo institucional.

| **Símbolo** | **Significado en el análisis** | **Valor documentado** |
|---|---|---:|
| $b$ | Factor de ramificación máximo: mayor número de acciones aplicables desde un estado | 5 |
| $d$ | Profundidad de la solución menos profunda | 6 |
| $m$ | Profundidad máxima del espacio de búsqueda | 16 |
| $N$ | Número de estados alcanzables desde el estado inicial | 935 |
| $b^*$ | Factor de ramificación efectivo equivalente | Calculado por algoritmo |

El valor $b = 5$ representa un máximo, por lo que no significa que todas las acciones estén disponibles en todos los estados. El modelo reporta un promedio de 3,9 acciones aplicables por estado.

Asimismo, $N = 935$ corresponde al total de estados alcanzables a distintas profundidades, hasta $m = 16$. Por esta razón, no debe combinarse directamente con $d = 6$ para calcular el factor de ramificación efectivo. Para este último se necesita el número de nodos generados durante la ejecución de cada algoritmo y la profundidad de la solución que encontró.

## Complejidad de BFS

La búsqueda en anchura (BFS) explora los nodos por niveles, comenzando por los estados más cercanos al inicial. En el peor caso, si la solución se encuentra a profundidad $d$ y el factor de ramificación máximo es $b$, puede generar una cantidad de nodos proporcional a:

$$
1+b+b^2+\cdots+b^d=O(b^d)
$$

Por tanto, su complejidad temporal es $O(b^d)$. Su complejidad espacial también es $O(b^d)$, porque debe conservar la frontera de búsqueda y los estados alcanzados para evitar repetir exploraciones.

BFS encuentra una solución de menor profundidad cuando las acciones se consideran con el mismo costo. Sin embargo, esto no garantiza encontrar la solución de menor costo acumulado cuando las acciones tienen costos diferentes, como ocurre en CampusGuard.

## Complejidad de DFS

La búsqueda en profundidad (DFS) continúa por una rama hasta que no puede avanzar y después retrocede para explorar alternativas. En un árbol de búsqueda con profundidad máxima $m$, su complejidad temporal es:

$$
O(b^m)
$$

La memoria de la versión clásica en árbol es:

$$
O(b \cdot m)
$$

Esto se debe a que conserva principalmente la ruta actual y las alternativas pendientes.

En una búsqueda sobre grafo, como la que registra estados explorados para evitar ciclos o repeticiones, el consumo real de memoria también incluye ese conjunto de estados visitados. Por ello, $O(b \cdot m)$ describe la cota clásica de DFS en árbol, pero no necesariamente toda la memoria de la implementación de CampusGuard.

DFS puede encontrar una solución rápidamente según el orden de las acciones, pero no garantiza que sea la de menor profundidad ni la de menor costo.

## Complejidad de A*

A* prioriza los nodos mediante la función:

$$
f(n)=g(n)+h(n)
$$

Donde:

- $g(n)$ representa el costo acumulado desde el estado inicial.
- $h(n)$ estima el costo restante hasta alcanzar la meta.
- $f(n)$ representa el costo estimado de una solución que pasa por el nodo $n$.

La heurística permite orientar la exploración hacia estados que parecen prometedores, reduciendo potencialmente el número de expansiones frente a una búsqueda no informada.

Sin embargo, A* no tiene una mejora polinómica garantizada por utilizar una heurística. En el peor caso, su tiempo y su memoria pueden crecer exponencialmente; una cota habitual para el análisis general es $O(b^d)$ para ambos recursos.

El comportamiento efectivo depende de la calidad de $h(n)$, de la distribución de costos y de la estructura del espacio de estados. La expresión $O(b^{d-k_h})$ puede utilizarse únicamente como una intuición simplificada del efecto de una heurística, no como una cota general garantizada.

En CampusGuard, la heurística documentada se construye sobre una abstracción del estado y un problema relajado. Para conservar la garantía de optimalidad de A*, debe ser admisible, es decir, no debe sobreestimar el costo real mínimo restante. La demostración específica de esa propiedad debe mantenerse junto con la documentación de la heurística.

## Comparación de las cotas

| **Algoritmo** | **Tiempo (peor caso)** | **Espacio (cota clásica)** | **Criterio de exploración** |
|---|---|---|---|
| BFS | $O(b^d)$ | $O(b^d)$ | Menor profundidad primero |
| DFS | $O(b^m)$ | $O(b \cdot m)$ en árbol; más el conjunto de visitados en búsqueda sobre grafo | Profundiza por una rama |
| A* | Exponencial; comúnmente $O(b^d)$ | Exponencial; comúnmente $O(b^d)$ | Menor $g(n)+h(n)$ primero |

Estas cotas corresponden al análisis general de los algoritmos. No deben confundirse con el número de estados alcanzables del modelo ni con los tiempos medidos en una ejecución concreta.

## Resultados experimentales disponibles

La siguiente tabla recoge los resultados comparativos registrados para el estado inicial y la meta del modelo. Los costos son unidades relativas de costo institucional definidas por las acciones; no representan horas reales. Los tiempos se obtuvieron con `benchmark.py`, como promedio de 100 ejecuciones (mediana de tres corridas), y pueden variar entre equipos.

| **Algoritmo** | **Nodos expandidos** | **Tiempo registrado** | **Costo del plan** |
|---|---:|---:|---:|
| BFS | 175 | 0,60 ms | 16 |
| DFS | 8 | 0,03 ms | 23 |
| A* | 136 | 0,66 ms | 14 |

En estos resultados, A* expandió 136 nodos frente a los 175 de BFS. La reducción relativa de expansiones fue:

$$
\frac{175-136}{175}\times 100 \approx 22,29\%
$$

A* obtuvo el menor costo registrado (14), mientras que BFS encontró un plan de menor profundidad, pero no de menor costo total. DFS expandió menos nodos en esta ejecución, aunque su plan tuvo un costo mayor (23). Por tanto, contar las expansiones por sí solo no permite concluir que un algoritmo haya encontrado una mejor solución.

El tiempo registrado de A* también fue mayor en esta corrida. Esto muestra que una reducción en el número de expansiones no implica necesariamente un menor tiempo de ejecución, ya que la gestión de prioridades y el cálculo de la heurística tienen un costo adicional.

Estas cifras deben actualizarse si cambia el código o se ejecuta un nuevo benchmark. Para una comparación reproducible, los tres algoritmos deben utilizar el mismo estado inicial, la misma meta y una convención uniforme de conteo. Un nodo expandido es aquel al que se le generan sus sucesores. El tiempo debe calcularse mediante múltiples ejecuciones, tal como establece la guía del repositorio.

## Factor de ramificación efectivo

El factor de ramificación efectivo ($b^*$) permite estimar el crecimiento del árbol de búsqueda a partir del número de nodos generados y de la profundidad de la solución encontrada. Representa el factor de ramificación constante que tendría un árbol hipotético para generar una cantidad equivalente de nodos hasta alcanzar dicha profundidad.

Su expresión matemática es:

$$
N = 1 + b^* + (b^*)^2 + ... + (b^*)^d
$$

Donde:

- $N$: número total de nodos generados durante la búsqueda.
- $b^*$: factor de ramificación efectivo.
- $d$: profundidad de la solución encontrada.

A partir de la instrumentación y ejecución de los tres algoritmos implementados para CampusGuard, se obtuvieron los siguientes resultados:

| **Algoritmo** | **Nodos generados ($N$)** | **Profundidad de la solución ($d$)** | **Factor de ramificación efectivo ($b^*$)** |
|---|---:|---:|---:|
| BFS | 786 | 6 | 2,825 |
| DFS | 24 | 8 | 1,233 |
| A* | 610 | 7 | 2,305 |

Los valores de $b^*$ se calcularon numéricamente, resolviendo la ecuación para cada algoritmo a partir del número de nodos generados y la profundidad de su solución.

Para mantener una convención uniforme, el conteo de nodos generados incluye el nodo inicial y los nodos sucesores creados durante la expansión, incluso cuando posteriormente se descartan por repetición. Estos conteos se obtuvieron mediante instrumentación del código, ya que las versiones originales no registraban directamente esta métrica para los tres algoritmos.

**Interpretación de los resultados:**

BFS obtuvo un factor de ramificación efectivo de 2,825, el más alto de los tres algoritmos. Esto refleja un mayor crecimiento del árbol de búsqueda en esta ejecución. DFS presentó el menor valor, con 1,233; sin embargo, esto no significa que sea necesariamente el algoritmo más eficiente, puesto que encontró una solución de mayor profundidad y costo.

Por su parte, A* obtuvo un factor de 2,305, inferior al de BFS. Esto coincide con la menor cantidad de nodos generados por A* frente a BFS. Además, A* encontró una solución de costo 14, inferior al costo 16 de BFS y al costo 23 de DFS.

En conjunto, los resultados muestran que A* ofrece un equilibrio favorable entre la exploración del espacio de búsqueda y la calidad de la solución encontrada. No obstante, el factor de ramificación efectivo debe interpretarse junto con la profundidad, el costo del plan, los nodos expandidos y el tiempo de ejecución, ya que por sí solo no determina el rendimiento global de un algoritmo.

## Consideraciones para interpretar los resultados

La complejidad Big O describe el crecimiento asintótico y no predice por sí sola cuál algoritmo será más rápido en una instancia pequeña. En CampusGuard, el espacio alcanzable está acotado y contiene 935 estados; por eso, las mediciones concretas también dependen de las estructuras de datos, del orden de generación de acciones, de la cola de prioridad de A* y del costo de evaluar la heurística.

La comparación debe considerar conjuntamente los nodos generados, los nodos expandidos, el tiempo de ejecución y el costo del plan. BFS favorece soluciones de menor profundidad; DFS puede hallar rápidamente una solución que no sea óptima; A* utiliza información heurística para orientar la búsqueda hacia un plan de menor costo y conserva esa garantía cuando su heurística es admisible y la implementación gestiona correctamente los costos y los estados alcanzados.

## Referencias

Russell, S., & Norvig, P. (2021). *Artificial intelligence: A modern approach* (4th ed.). Pearson.

AIMA-Python. (s. f.). *Python implementation of algorithms from Russell and Norvig's “Artificial Intelligence: A Modern Approach”*. GitHub. https://github.com/aimacode/aima-python
