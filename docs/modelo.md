# Modelo del problema

## Abstracción del entorno

El entorno real de CampusGuard es parcialmente observable, estocástico, secuencial, dinámico y en parte continuo. El agente solo ve lo que registran los sistemas institucionales, la misma intervención puede funcionar con un estudiante y fracasar con otro, la situación de cada estudiante cambia mientras el agente decide y el riesgo es una magnitud que varía de forma gradual. Los algoritmos de búsqueda que se usan aquí suponen, en cambio, un entorno completamente observable, determinista, estático y discreto, en el que el agente puede calcular de antemano la secuencia de acciones que lo lleva a la meta (Russell y Norvig, 2021).

Para cerrar esa distancia, el modelo se apoya en cuatro supuestos. El primero es que el agente planifica sobre una fotografía de los registros tomada en un momento dado, de modo que el estado del estudiante se considera conocido en el instante de planear. El segundo es que cada intervención produce siempre su efecto esperado; la variabilidad en la respuesta de cada estudiante se atiende volviendo a planificar cuando llegan datos nuevos. El tercero es que el entorno no cambia mientras el agente calcula el plan. El cuarto es que las magnitudes continuas, como el nivel de riesgo, se expresan en niveles enteros. Con estos supuestos el entorno queda determinista y discreto, y conserva su carácter secuencial, ya que cada acción condiciona las que vienen después.

## Estado, meta y acciones

Cada estudiante se representa con el vector de estado (r, a, c, t, b). En él, r es el nivel de riesgo académico, de 0 a 10; a es el número de inasistencias del último mes, de 0 a 8, que equivale a dos clases semanales durante cuatro semanas; c es el nivel de carga académica, de 1 (la mínima) a 4 (la completa); t es el número de tutorías asignadas en el periodo, de 0 a 5; y b indica si ya se notificó a bienestar universitario (0 o 1).

El estado inicial es (10, 8, 4, 0, 0), que corresponde a un estudiante con riesgo máximo, ocho inasistencias, carga completa y ninguna intervención previa. La prueba de meta se cumple cuando r ≤ 2 y a ≤ 1, es decir, cuando el estudiante alcanza un riesgo bajo y una asistencia regular. La tabla siguiente presenta las acciones disponibles, sus condiciones de aplicación, el modelo de transición y su costo.

| Acción | Condición | Efecto sobre el estado | Costo |
|---|---|---|---|
| TUTORIA | r > 0 y t < 5 | r − 1, t + 1 | 1 |
| SEGUIMIENTO | a > 0 | a − 1 | 1 |
| ASESORIA | r > 0 y a > 0 | r − 1, a − 1 | 2 |
| BIENESTAR | b = 0 | r − 2, a − 3, b = 1 | 4 |
| AJUSTE_CARGA | c > 1 y r > 0 | r − 3, c − 1 | 5 |

Ningún valor desciende por debajo de 0. SEGUIMIENTO es un contacto directo del docente con el estudiante, ASESORIA es una sesión de consejería académica y AJUSTE_CARGA corresponde a cancelar o aplazar una asignatura.

## Función de costo

El costo de un plan es la suma de los costos de sus acciones. Estos costos expresan, en unidades relativas, los recursos institucionales y el impacto sobre el estudiante de cada intervención. Una tutoría o un contacto del docente demandan poco tiempo de personal. La notificación a bienestar abre un caso con un profesional. El ajuste de carga es la intervención más costosa porque exige un trámite administrativo y retrasa el avance del estudiante en su plan de estudios. De esta forma, las acciones con mayor efecto sobre el riesgo resultan menos eficientes por unidad de mejora, y el agente debe sopesar el número de acciones frente al costo total del plan.

## Características del espacio de estados

Toda acción reduce el riesgo, las inasistencias o la carga, o agota la notificación a bienestar, así que el espacio no tiene ciclos y todo camino es finito. Desde el estado inicial se alcanzan 935 estados, con un factor de ramificación máximo b = 5 (en promedio, 3,9 acciones aplicables por estado), una profundidad máxima m = 16 y una solución menos profunda a d = 6 acciones. El costo óptimo para llegar a la meta es 14. Estos parámetros son la base del análisis de complejidad.

## Referencias

Russell, S., & Norvig, P. (2021). *Artificial intelligence: A modern approach* (4th ed.). Pearson.
