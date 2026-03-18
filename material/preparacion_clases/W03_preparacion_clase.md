# Professor's Class Brief — W03
## Big Data, OLTP/OLAP, ETL y Síntesis de la Unidad 1
**Curso**: Big Data y Analytics · ICOM E015 · Universidad San Sebastián
**Unidad**: 1 — Sistemas de Información en el Contexto Empresarial
**Duración**: 1 hora 20 minutos (clase magistral) + Solemne 1 (segunda parte)

---

## 1. Core Thesis

Esta sesión tiene una doble función: cierra la Unidad 1 con el argumento de mayor densidad tecnológica del bloque, y somete a evaluación todo lo aprendido en las tres semanas anteriores. La tesis que articula el contenido nuevo es que **los sistemas vistos hasta ahora —TPS, BI, CMI— no pueden coexistir en una única base de datos sin degradar mutuamente su desempeño**, y que la solución industrial a este problema es la arquitectura OLTP → ETL → Data Warehouse → BI. Esta arquitectura no es un detalle técnico optativo: es la razón por la que el CMI de Roberto puede mostrar datos frescos cada mañana sin bloquear el sistema de pedidos que Sofía usa en tiempo real.

El segundo argumento es que el fenómeno del Big Data no es simplemente "mucho dato": es el conjunto de tensiones —Volumen, Velocidad, Variedad, Veracidad, Valor— que aparece cuando el crecimiento de TechStyle convierte un problema de análisis de datos convencional en un problema de ingeniería de datos. Estas tensiones tienen implicancias directas sobre los costos de arquitectura, la calidad de los datos y la latencia de las decisiones. El Big Data no cambia el propósito del sistema de información; cambia las condiciones bajo las cuales ese propósito debe cumplirse.

El tercer argumento, transversal a toda la sesión, es de síntesis: las tres semanas de la Unidad 1 construyen una cadena conceptual única —Dato → Información → SI → Tipos de SI → CMI → Calidad de Datos → ETL → DW → Decisión— y cada concepto de la sesión de hoy es la extensión lógica de los anteriores. Esta sesión es, en ese sentido, el cierre argumentativo de la unidad: los estudiantes deben poder ver, al terminar, que todo el andamiaje conceptual forma un sistema coherente, no una colección de temas aislados.

---

## 2. Narrative Roadmap

La sesión se articula en cuatro fases. Las dos primeras corresponden al contenido nuevo; la tercera es la síntesis de la unidad; la cuarta es la evaluación. El tiempo es ajustado: la disciplina narrativa es crítica.

### Fase 1 — El Problema del Crecimiento: TechStyle en 2028 y el Big Data (≈ 25 min)

La clase abre con una proyección: TechStyle en 2028 tiene 8,5 millones de clientes y 340.000 pedidos diarios. El Excel de María ya no abre. El BI tarda 4 horas en generar un reporte. El objetivo de esta fase no es enseñar las 5 V por sí mismas, sino demostrar que el crecimiento cuantitativo de los datos produce un cambio cualitativo en los desafíos de gestión informacional. Las 5 V son el vocabulario para nombrar esos desafíos, no un fin en sí mismas.

El punto pedagógico crítico es la **V de Valor**: TechStyle tiene 180TB de datos históricos pero solo usa el 12% para tomar decisiones. Este es el argumento que conecta el Big Data con la Unidad 1 completa: no basta con tener datos (V1), generarlos rápido (V2) y en formatos diversos (V3) con buena calidad (V4). Si no existe la arquitectura y el proceso para extraer valor de ellos, el volumen es una carga, no un activo. Esta tensión entre datos disponibles y datos utilizados es la motivación directa para el ETL y el Data Warehouse.

El ejercicio de clasificación ("¿Qué V representa cada desafío?") sirve como verificación activa antes de avanzar. Es rápido y permite identificar si los estudiantes están procesando las V como categorías de análisis o como definiciones para memorizar.

### Fase 2 — La Arquitectura de la Solución: OLTP, OLAP, DW y ETL (≈ 30 min)

Esta es la fase de mayor densidad conceptual. Se estructura en tres movimientos secuenciales que deben mantenerse en ese orden porque cada uno presupone el anterior.

**Movimiento 1 — OLTP vs. OLAP**: la distinción no es entre sistemas "viejos" y "nuevos"; es entre sistemas optimizados para operaciones unitarias en tiempo real (OLTP) versus sistemas optimizados para consultas analíticas sobre grandes volúmenes históricos (OLAP). El argumento central —que no se puede optimizar la misma base de datos para los dos usos simultáneamente— no es una limitación tecnológica superable: es una consecuencia directa de las estructuras de índices y bloqueos de filas que hacen que un INSERT rápido y un GROUP BY sobre millones de filas sean mutuamente excluyentes en la misma arquitectura. Si Juan ejecuta su consulta analítica en la BD de Sofía, los pedidos dejan de procesarse. Este es el problema que justifica la existencia del Data Warehouse.

**Movimiento 2 — El Data Warehouse y sus capas**: el DW no es simplemente una base de datos grande; es una base de datos diseñada exclusivamente para análisis, con una arquitectura en capas (Staging → Integración → Data Marts) que implementa exactamente el proceso de calidad de datos visto en W02. La capa de Staging recibe los datos brutos tal como vienen del OLTP (zona de cuarentena). La capa de integración aplica las transformaciones de calidad (estandarizar "Santiago" / "Stgo." / "RM" → "Metropolitana"). Los Data Marts exponen los datos limpios y organizados por dominio (ventas, clientes, logística) a las herramientas de BI. Esta arquitectura en capas es la respuesta organizacional a los problemas de calidad identificados en W02.

**Movimiento 3 — El ETL**: el proceso Extraer–Transformar–Cargar es el mecanismo que conecta el OLTP con el DW. El punto pedagógico clave es que la fase de Transformación no es solo limpieza técnica: requiere entender las reglas de negocio que definen qué es un dato correcto, cuándo una fila debe eliminarse, y cómo deben fusionarse registros duplicados. Esta es la misma lógica de las dimensiones de calidad de W02, ahora operacionalizada como un proceso automático y repetible.

**Conexión con herramientas conocidas**: el cierre de esta fase conecta la arquitectura industrial con lo que los estudiantes ya dominan. Power Query es un ETL de escritorio. Power BI se conecta a la capa de presentación del DW, no al OLTP. El modelo estrella que construyeron en el Lab W03 es el esquema típico del Data Mart. MySQL (que verán en la Unidad 3) es tanto el OLTP como el sustrato del DW en entornos medianos. Este mapeo entre conceptos nuevos y herramientas conocidas es fundamental para que los estudiantes vean el semestre como un sistema coherente y no como una secuencia de módulos independientes.

### Fase 3 — Síntesis de la Unidad 1 (≈ 10 min)

La sesión dedica 10 minutos explícitos a la síntesis de las tres semanas. El instrumento es la tabla de síntesis (W01: jerarquía y componentes; W02: tipos de SI y CMI; W03: Big Data y ETL) y el hilo conductor que une todas las semanas: TechStyle necesita los **datos correctos**, en el **sistema correcto**, para el **actor correcto**, en el **momento correcto** → para tomar **decisiones correctas**.

La actividad de repaso "Caso ServiRápido" materializa esta síntesis: obliga a los estudiantes a aplicar simultáneamente conceptos de las tres semanas (tipos de SI, CMI, ETL) a un contexto nuevo, verificando si han incorporado el marco como herramienta de análisis o solo como contenido para la evaluación. Tiene una doble función: repasar y calibrar el nivel de preparación para la Solemne 1.

---

#### Caso ServiRápido — Enunciado y Respuesta de Referencia

**Enunciado (presentar a los estudiantes)**

> ServiRápido es una empresa de delivery de comida con sede en Temuco. Fundada en 2019, comenzó con 12 repartidores y hoy opera con 380, procesa 4.200 pedidos diarios y tiene convenio con 640 restaurantes en tres regiones. La empresa usa un sistema para registrar pedidos, otro para gestionar repartidores y un tercero para cobrar a los restaurantes. Los tres sistemas fueron desarrollados por proveedores distintos y no se comunican entre sí.
>
> Valentina, la gerenta de operaciones, necesita responder tres preguntas cada lunes: ¿Cuántos pedidos se entregaron tarde la semana pasada?, ¿qué restaurantes tienen mayor tasa de cancelación? y ¿cuál es el tiempo promedio de entrega por zona?. Hoy, Valentina obtiene esas respuestas exportando tres Excel distintos, cruzándolos a mano y calculando en una planilla propia. El proceso le toma entre 3 y 4 horas cada semana.
>
> Además, el equipo de TI detectó que la columna "tiempo de entrega" se registra en minutos en el sistema de repartidores pero en segundos en el sistema de pedidos. El campo "nombre del restaurante" tiene 47 variantes ortográficas distintas para los mismos 640 locales.
>
> **Preguntas:**
> 1. ¿Qué tipo de SI es el sistema de registro de pedidos de ServiRápido? ¿Y la planilla de Valentina?
> 2. Diseña tres KPIs que debería incluir un CMI para Valentina. Para cada KPI indica el nombre, la fórmula y la fuente de datos.
> 3. ¿Qué problema de calidad de datos afecta a ServiRápido? Identifica al menos dos dimensiones de calidad comprometidas.
> 4. Valentina quiere automatizar su reporte semanal. ¿Qué arquitectura le recomendarías? Describe brevemente el rol del OLTP, el ETL y el DW en la solución.
> 5. El equipo de TI propone que Juan, el analista de datos, se conecte directamente a la base de datos de pedidos para generar el reporte de Valentina. ¿Es una buena decisión? ¿Por qué sí o por qué no?

---

**Respuesta de referencia (uso del profesor)**

**Pregunta 1 — Tipos de SI**

El sistema de registro de pedidos es un **TPS (Transaction Processing System)** u **OLTP**: registra operaciones unitarias en tiempo real (un pedido = una transacción), involucra al nivel operativo (repartidores, restaurantes) y su prioridad es velocidad y consistencia en cada escritura. La planilla de Valentina es un **DSS (Decision Support System)** rudimentario o, en el lenguaje del curso, un sistema de **BI artesanal**: consolida datos de múltiples fuentes para apoyar decisiones de nivel táctico. No es un CMI formal porque no está automatizado, no tiene indicadores estandarizados y depende del trabajo manual de una persona.

**Pregunta 2 — KPIs para el CMI de Valentina**

| KPI | Fórmula | Fuente |
|---|---|---|
| **Tasa de entrega a tiempo** | (Pedidos entregados en ≤ tiempo prometido / Total pedidos entregados) × 100 | Sistema de repartidores + sistema de pedidos |
| **Tasa de cancelación por restaurante** | (Pedidos cancelados por restaurante / Total pedidos del restaurante) × 100 | Sistema de pedidos |
| **Tiempo promedio de entrega por zona** | Suma(tiempo de entrega por zona) / Total pedidos de esa zona | Sistema de repartidores (una vez estandarizado a minutos) |

Nota para el profesor: los estudiantes deben justificar la fuente. Si dicen "el sistema" sin especificar cuál, pedir que identifiquen cuál de los tres sistemas tiene el dato. Esto conecta con la necesidad del ETL para integrar fuentes heterogéneas.

**Pregunta 3 — Calidad de datos**

Dimensiones comprometidas (W02):

- **Consistencia**: el tiempo de entrega está en unidades distintas en dos sistemas (minutos vs. segundos). Un JOIN directo produciría datos incorrectos sin transformación previa. Es inconsistencia entre sistemas.
- **Exactitud / Unicidad**: las 47 variantes ortográficas del nombre del restaurante impiden agrupar correctamente. Un reporte por restaurante mezclaría filas del mismo local bajo identidades distintas, generando duplicados analíticos. Es un problema de estandarización que el ETL debe resolver en la capa de integración del DW.

Dimensión adicional válida: **Completitud**, si hay pedidos sin tiempo de entrega registrado (repartidores que olvidan marcar la entrega en el sistema).

**Pregunta 4 — Arquitectura recomendada**

ServiRápido necesita la arquitectura **OLTP → ETL → DW → BI**:

- **OLTP** (los tres sistemas actuales): continúan operando como están. No se modifican. Su función es registrar operaciones en tiempo real; no deben usarse para análisis.
- **ETL** (proceso automático, idealmente nocturno): extrae los datos de los tres sistemas, aplica las transformaciones necesarias (convertir segundos a minutos, estandarizar nombres de restaurantes a una forma canónica, resolver el campo "zona" si tiene variantes) y carga los datos limpios en el DW. Este proceso reemplaza las 3–4 horas semanales de Valentina.
- **DW** (repositorio analítico centralizado): almacena los datos limpios e integrados de los tres sistemas en un modelo optimizado para consultas. La capa de Staging recibe los datos brutos; la capa de integración aplica las transformaciones; el Data Mart de operaciones expone exactamente las tablas que necesita el BI de Valentina.
- **BI** (Power BI o similar): se conecta al Data Mart, no a los OLTP. El reporte de Valentina se actualiza automáticamente cada lunes sin intervención manual.

**Pregunta 5 — Conexión directa al OLTP**

No es una buena decisión, por dos razones:

1. **Degradación operacional**: la consulta analítica de Juan (`GROUP BY`, `JOIN` entre tablas de pedidos y repartidores) requiere leer grandes volúmenes de datos y mantiene bloqueos sobre esas filas mientras se ejecuta. Esto interfiere con los INSERT de nuevos pedidos, generando latencia o bloqueos en el sistema operativo. Para una empresa con 4.200 pedidos diarios, un bloqueo de 20–30 minutos durante el reporte es operacionalmente inaceptable.
2. **Datos sin limpiar**: el OLTP tiene las inconsistencias descritas (unidades distintas, 47 variantes de nombres). Un reporte construido directamente sobre esos datos producirá resultados incorrectos sin que Juan necesariamente lo note. El reporte puede ser técnicamente funcional pero analíticamente erróneo.

La solución correcta es que Juan se conecte al **Data Mart** del DW, donde los datos ya fueron limpiados y estandarizados por el ETL. Si no existe aún el DW, la solución mínima es que Juan aplique las transformaciones en Power Query antes de construir el reporte, documentando las reglas de transformación para que sean reproducibles.

### Fase 4 — Solemne 1 (segunda parte de la sesión)

La evaluación individual ocupa la segunda parte de la sesión. Antes de iniciar, el profesor debe explicitar el énfasis: **razonamiento y justificación, no memorización**. Las preguntas de la Solemne no preguntan definiciones; preguntan por aplicación de conceptos a casos nuevos, diseño de KPIs para contextos específicos, y diagnóstico de problemas de calidad en datasets ficticios. Un estudiante que memorizó todas las definiciones pero no entiende por qué el CMI depende del ETL tendrá dificultades.

---

## 3. Key Visual Evidence

| Visual | Archivo | Argumento que ilustra |
|---|---|---|
| **Diagrama OLTP → ETL → DW → BI → CMI** | Slide texto (código ASCII en la presentación) | Muestra el flujo completo de datos desde la operación hasta la decisión. Es el visual más importante de la sesión: integra todos los conceptos de la Unidad 1 en una arquitectura funcional única. |
| **Tabla OLTP vs. OLAP** | Slide tabla | Contrasta las características de los dos sistemas en cinco dimensiones (propósito, operación SQL, volumen, usuario, ejemplo TechStyle). Demuestra que la incompatibilidad no es superficial sino estructural. |
| **Diagrama de las 3 capas del DW** | Slide texto | Muestra cómo las etapas Staging → Integración → Data Marts implementan el proceso de calidad de datos del W02 como arquitectura. Conecta la calidad de datos (W02) con la arquitectura técnica (W03). |
| **Pirámide Organizacional de TechStyle** | `img/piramide_organizacional_techstyle.jpg` | Reutilizada de W01–W02, pero ahora con el OLTP en la base, el ETL como proceso de ascenso, el DW en la capa táctica y el CMI en el vértice estratégico. El mismo visual, una capa más de interpretación. |

**Nota para el profesor**: si el tiempo es escaso y debe elegir un solo visual para desarrollar, el diagrama de flujo completo (OLTP → ETL → DW → BI → CMI → Decisión) es el más importante. Condensa el argumento de toda la sesión y sirve como mapa conceptual para la Solemne 1. Los demás visuales pueden describirse verbalmente si es necesario.

---

## 4. Discussion Benchmarks

**Pregunta 1 — Comprensión por analogía** *(después de las 5 V del Big Data)*
> "Un hospital regional acumula tomografías, historiales médicos en texto, registros de medicamentos y datos de sensores de UCI. ¿Cuál de las 5 V es el desafío más crítico para ese hospital? ¿Cambiaría su respuesta si el hospital fuera el Hospital Clínico de la Universidad de Chile versus una posta rural de La Araucanía?"

Esta pregunta fuerza a aplicar las 5 V como herramienta de diagnóstico, no como lista de definiciones, y a reconocer que la V crítica depende del contexto organizacional específico.

**Respuesta de referencia:**
- **Hospital Clínico de la U. de Chile**: la V más crítica es **Variedad**. El desafío no es solo el volumen (aunque es alto), sino que cada tipo de dato —tomografías DICOM, texto clínico libre, series temporales de sensores de UCI, tablas de medicamentos— requiere pipelines de procesamiento y sistemas de almacenamiento completamente distintos. Integrarlos en un único repositorio analítico coherente es el cuello de botella arquitectural dominante.
- **Posta rural de La Araucanía**: la V más crítica es **Veracidad**. El volumen es bajo, la variedad es manejable, pero el personal reducido y sin formación en gestión de datos introduce inconsistencias sistemáticas (diagnósticos registrados a mano, campos omitidos, ortografía variable). Con poca capacidad de TI para corregirlos, los datos de baja calidad invalidan cualquier análisis posterior.
- **Argumento central**: las 5 V son un marco de diagnóstico, no una lista de problemas universales. La V crítica depende del tamaño, la madurez tecnológica y los procesos operativos de la organización específica. El primer trabajo del analista de datos es identificar cuál V es el cuello de botella, no asumir que son todas iguales.

**Pregunta 2 — Pensamiento causal sistémico** *(después de OLTP vs. OLAP)*
> "Sofía registra un pedido en el sistema OLTP de TechStyle. Juan necesita en ese mismo instante el reporte de ventas del mes. ¿Por qué no puede Juan simplemente 'leer' la misma base de datos donde Sofía está escribiendo? ¿Qué pasaría operativamente si se lo permitieran?"

Obliga a comprender la incompatibilidad OLTP–OLAP no como una regla a memorizar sino como una consecuencia lógica del diseño de bases de datos. Anticipa la discusión sobre bloqueos de filas y concurrencia que los estudiantes verán en detalle en la Unidad 3 (transacciones ACID, W15).

**Respuesta de referencia:**
- **¿Por qué no puede Juan leer la misma BD?** La consulta analítica de Juan (`SELECT ... GROUP BY` sobre millones de filas) requiere leer grandes porciones de la tabla y mantiene bloqueos compartidos sobre esas filas durante toda la ejecución, que puede durar varios minutos. Al mismo tiempo, el INSERT de Sofía necesita adquirir un bloqueo de escritura sobre la misma tabla para garantizar consistencia (principio ACID que verán en W15). Si ambas operaciones compiten en la misma base de datos, el motor debe elegir: o bloquea a Sofía mientras Juan lee, o cancela la consulta de Juan para liberar el paso. En cualquier caso, uno de los dos pierde.
- **¿Qué pasaría operativamente?** Si se permite, los pedidos dejan de procesarse en tiempo real mientras el reporte está calculando. Para un e-commerce con 340.000 pedidos diarios, un bloqueo de 4 horas equivale a tens de miles de pedidos no procesados, clientes con compras fallidas y pérdida directa de ingresos. Es el equivalente a cerrar la caja de un supermercado para que el contador pueda revisar las ventas del mes en ese mismo cajón.
- **La solución**: separar los sistemas. OLTP para operar (Sofía escribe sin contención), DW para analizar (Juan lee sin impactar operaciones), ETL como puente nocturno que mueve los datos entre ambos.

**Pregunta 3 — Diseño de arquitectura** *(después del Data Warehouse y ETL)*
> "TechStyle tiene tres equipos distintos que construyeron el sistema de ventas, el sistema de clientes y el sistema de logística en momentos diferentes. Los tres usan nombres distintos para la misma región ('RM', 'Santiago', 'Metropolitana') y formatos distintos para las fechas. ¿En qué capa del DW se resuelve este problema? ¿Quién debería tomar esa decisión: el equipo de TI, el área de ventas, o el Data Steward de W02?"

Conecta la arquitectura técnica del DW con el gobierno de datos visto en W02 y fuerza a pensar en quién tiene autoridad sobre las definiciones de datos. No hay una respuesta única correcta; el debate entre solución técnica y solución organizacional es pedagógicamente productivo.

**Respuesta de referencia:**
- **¿En qué capa del DW?** En la **capa de integración** (segunda capa). La capa de Staging recibe los datos tal como llegan de cada OLTP, incluyendo todas las inconsistencias. Es en la capa de integración donde se aplican las reglas de estandarización: "RM", "Santiago" y "Metropolitana" convergen en un único valor canónico. Los Data Marts (tercera capa) ya reciben datos limpios y no saben que alguna vez existieron las variantes.
- **¿Quién toma la decisión?** El **Data Steward**, no el equipo de TI. Esta es la distinción clave: TI puede *implementar* la transformación (`REPLACE "RM" WITH "Metropolitana"`), pero no puede *decidir* si "Santiago" como ciudad y "Metropolitana" como región son la misma cosa o no en el contexto de negocio. Esa decisión requiere conocimiento del negocio y autoridad sobre la definición oficial del dato. El área de ventas tiene el conocimiento de negocio pero puede tener un interés particular (su región puede quedar mejor o peor según cómo se agrupe). El Data Steward actúa como árbitro neutral con mandato organizacional explícito.
- **Punto de debate productivo**: ¿qué pasa si TI toma la decisión sin consultar? Puede generar una estandarización técnicamente correcta pero analíticamente incorrecta (por ejemplo, fusionar "Santiago" como ciudad con datos de toda la Región Metropolitana, mezclando granularidades distintas). Este error no se ve hasta que alguien nota que los datos no cuadran con la realidad que conoce del negocio.

**Pregunta 4 — Evaluación estratégica** *(durante la síntesis)*
> "TechStyle acaba de invertir $500 millones en implementar un Data Warehouse en la nube. Roberto tiene acceso a un dashboard con 47 KPIs actualizados cada hora. Sin embargo, el equipo de logística sigue registrando las entregas con un día de atraso porque el sistema OLTP no los obliga a registrar en tiempo real. ¿Cuál de las 5 V es el problema? ¿Sirve de algo el DW en ese contexto?"

Demuestra que la arquitectura técnica más sofisticada no resuelve problemas organizacionales o de procesos. Conecta la V de Oportunidad (veracidad temporal) con el concepto de gobierno de datos y con la calidad de datos de W02. Introduce el argumento de que la tecnología es condición necesaria pero no suficiente para la toma de decisiones de calidad.

**Respuesta de referencia:**
- **¿Cuál V es el problema?** **Veracidad**, específicamente en su dimensión de **Oportunidad** (uno de los atributos de calidad de datos de W02). Los datos existen, no hay problema de volumen ni variedad, pero llegan con 24 horas de retraso al OLTP, lo que hace que el dato sea temporalmente incorrecto en el momento en que se necesita para tomar decisiones.
- **¿Sirve de algo el DW?** Sí, pero solo parcialmente. El DW es útil para **análisis históricos**: tendencias de entrega de los últimos 6 meses, tasa de retrasos por zona, rendimiento de transportistas en el año. No sirve para **alertas operacionales en tiempo real**: detectar que hoy hay 1.200 pedidos sin confirmar entrega no es posible si el dato llega mañana. El dashboard de Roberto muestra KPIs "actualizados cada hora" que en realidad reflejan la realidad de hace 24 horas para todo lo relacionado con logística.
- **Conclusión clave**: los $500 millones en tecnología no resolvieron un problema de **proceso y gobierno organizacional**: el equipo de logística no registra en tiempo real porque nadie los obliga o incentiva a hacerlo. La arquitectura técnica es condición necesaria pero no suficiente. La solución real requiere una decisión organizacional (política de registro obligatorio en tiempo real) antes que una decisión tecnológica.

**Pregunta 5 — Síntesis y proyección profesional** *(al cierre, antes de la Solemne)*
> "Si en su primer trabajo como analistas de datos les piden construir un reporte mensual de ventas para el gerente comercial, ¿de qué sistema tomarían los datos: del OLTP, del DW o de Power BI directamente? ¿Qué preguntas harían antes de conectar la primera consulta?"

Personaliza la arquitectura técnica en el contexto de la práctica profesional. Hace visible que las preguntas correctas antes de construir un reporte son preguntas sobre arquitectura de datos, no solo sobre visualización. Calibra si los estudiantes han internalizado el flujo OLTP → ETL → DW → BI como una cadena que el analista debe comprender, no solo usar.

**Respuesta de referencia:**
- **¿De qué sistema?** Del **DW** (o del Data Mart de ventas, si existe). No del OLTP: conectarse al OLTP para un reporte analítico degrada el rendimiento operacional y expone datos brutos sin limpiar (las mismas inconsistencias que corrigieron en el Lab W03). No de Power BI "directamente": Power BI es una herramienta de visualización, no una fuente de datos; siempre se conecta a algo (OLTP, DW, Excel, API), y ese "algo" es lo que importa elegir bien.
- **¿Qué preguntas hacer antes de conectar?**
  1. *¿Existe un DW o Data Mart de ventas?* Si no existe, ¿hay un proceso ETL que limpie los datos del OLTP antes de exponerlos?
  2. *¿Cuál es la definición oficial de "venta"?* ¿Incluye devoluciones? ¿Solo pedidos confirmados o también pendientes? (Gobierno de datos)
  3. *¿Con qué frecuencia se actualiza el DW?* Si el ETL es nocturno y el gerente pide datos del día, el DW no sirve sin un complemento.
  4. *¿Existen medidas DAX o métricas ya definidas y validadas?* Reutilizarlas garantiza consistencia con otros reportes de la empresa.
  5. *¿Qué período y granularidad necesita el gerente?* ¿Mensual por región, por producto, por vendedor? La respuesta determina qué tablas del modelo estrella son necesarias.
- **Por qué estas preguntas son de arquitectura, no de visualización**: un analista que salta directamente a Power BI sin hacerse estas preguntas construirá un reporte técnicamente funcional pero analíticamente incorrecto o inconsistente con los reportes del resto de la empresa. Las preguntas correctas son las que mapean el requerimiento del negocio al eslabón correcto de la cadena OLTP → ETL → DW → BI.

---

## 5. Essential Vocabulary

Los siguientes términos constituyen el capital conceptual mínimo al término de la sesión y forman la base léxica de la Solemne 1. Se recomienda al profesor verificar 3–4 términos al azar durante el repaso de síntesis antes de iniciar la evaluación.

| Término | Definición operacional en el contexto del curso |
|---|---|
| **Big Data** | Fenómeno caracterizado por datos que exceden la capacidad de los sistemas de procesamiento convencionales en al menos una de las 5 V (Volumen, Velocidad, Variedad, Veracidad, Valor). No es un tamaño absoluto: es una relación entre el dato y la capacidad del sistema que debe procesarlo. |
| **Las 5 V** | Marco analítico para diagnosticar desafíos de Big Data. Volumen (cantidad), Velocidad (frecuencia de generación), Variedad (formatos heterogéneos), Veracidad (confiabilidad y calidad) y Valor (fracción del dato que genera insight accionable). |
| **OLTP** (Online Transaction Processing) | Arquitectura de base de datos optimizada para operaciones transaccionales unitarias en tiempo real: INSERT, UPDATE, DELETE de pocas filas, con tiempos de respuesta menores a 100ms. Usuario típico: nivel operativo (Sofía). |
| **OLAP** (Online Analytical Processing) | Arquitectura de base de datos optimizada para consultas analíticas sobre grandes volúmenes históricos: SELECT con GROUP BY, JOINs y agregaciones sobre millones de filas. Usuario típico: nivel táctico-estratégico (Juan, Roberto). |
| **Data Warehouse (DW)** | Base de datos diseñada exclusivamente para OLAP. Integra múltiples fuentes OLTP en un repositorio histórico unificado. Arquitectura en tres capas: Staging (datos brutos), Integración (datos limpios y unificados), Data Marts (datos organizados por dominio analítico). |
| **Data Mart** | Subconjunto del DW organizado para un dominio específico (ventas, clientes, logística). Los analistas y el BI se conectan al Data Mart de su área, no al DW completo ni al OLTP. |
| **ETL** (Extract, Transform, Load) | Proceso que mueve datos desde los sistemas OLTP hacia el DW en tres fases: Extraer (conectar con las fuentes), Transformar (limpiar, estandarizar y enriquecer) y Cargar (insertar en el DW). En producción se ejecuta automáticamente de forma periódica (batch) o continua (streaming). |
| **Batch ETL** | Modalidad de ETL en la que el proceso se ejecuta periódicamente (típicamente en horario nocturno) sobre el acumulado de datos desde la última ejecución. Contrasta con el ETL en streaming, que procesa eventos en tiempo real. |
| **Modelo Estrella** | Esquema de organización del Data Mart con una tabla de hechos central (transacciones) rodeada de tablas de dimensiones (clientes, productos, tiempo, región). Optimizado para consultas analíticas con JOINs radiales. |
| **Staging (área de preparación)** | Primera capa del DW donde se copian los datos brutos del OLTP sin transformar. Actúa como zona de cuarentena: garantiza que los datos de origen no se modifican y permite repetir las transformaciones si se detectan errores. |

---

## Notas de Coordinación Docente

- **Conexión con W01 y W02**: esta sesión presupone el dominio de la jerarquía dato–información–decisión, los 5 componentes del SI, la taxonomía de tipos de SI, el CMI y las cuatro dimensiones de calidad de datos. Si la Solemne 1 evidencia debilidades sistemáticas en alguno de estos conceptos, es señal de que el Lab W02 no logró consolidarlos y deberá reforzarse en las primeras sesiones de la Unidad 2.
- **Gestión del tiempo**: la presión de tiempo es la principal dificultad de esta sesión. El contenido nuevo (Big Data, OLTP/OLAP, DW, ETL) podría extenderse 90 minutos sin dificultad, pero debe comprimirse en 55 minutos para dejar margen a la síntesis y la Solemne. La disciplina es no profundizar en detalles de implementación del ETL (transformaciones específicas de Power Query) sino en el argumento arquitectural: por qué el flujo existe y qué problema resuelve.
- **La Solemne 1**: el 30% de ponderación (10% control acumulado + 20% prueba escrita) implica que los estudiantes con bajo rendimiento en W02 pueden recuperar terreno. El énfasis en razonamiento sobre memorización es intencional y debe comunicarse explícitamente antes de la evaluación para evitar la ansiedad que genera en estudiantes con buen rendimiento memorizador pero menor capacidad de análisis aplicado.
- **Conexión con la Unidad 2**: la sesión cierra señalando que la Unidad 2 responde a la pregunta "¿cómo se diseña la estructura de datos que alimenta el OLTP?". Esto ancla los conceptos de modelado (diagrama ER, modelo relacional, normalización) en un propósito funcional que los estudiantes ya comprenden: construir bien el OLTP es condición previa para que el ETL y el CMI funcionen correctamente.
- **Laboratorio W03**: el Lab materializa el proceso ETL completo usando Power BI y Power Query. Los estudiantes recibirán exactamente las tres fuentes OLTP mencionadas en clase (`oltp_ventas.csv`, `oltp_clientes.csv`, `oltp_productos.csv`) con las inconsistencias descritas (columnas con nombres distintos, formatos de fecha heterogéneos, variantes de región). El script de referencia `labs/scripts/W03_etl_mini.py` reproduce el flujo completo en Python para uso del docente.

---

## 6. Online Reference Materials

Recursos organizados por los cuatro bloques temáticos de la sesión. Se indica el propósito pedagógico específico de cada uno.

### 6.1 Big Data y las 5 V

**IBM — "What is Big Data?"**
- URL: https://www.ibm.com/think/topics/big-data
- Relevancia: descripción actualizada del fenómeno Big Data desde una perspectiva empresarial, incluyendo las 5 V con ejemplos industriales concretos. IBM tiene la ventaja de ser simultáneamente fuente académicamente respetable y proveedor de soluciones de Big Data en empresas chilenas (plataforma Cloud). Útil para mostrar que las definiciones del curso coinciden con el estándar de la industria.

**O'Reilly — "What is Big Data?" (Mike Loukides, 2010)**
- URL: https://www.oreilly.com (buscar el artículo "What is Big Data?" de Mike Loukides)
- Relevancia: uno de los textos fundacionales que popularizó el término "Big Data" en la industria tecnológica. La perspectiva es histórica y ayuda a situar por qué el concepto emergió en ese momento específico (explosión de datos generados por usuarios de internet). Útil para el profesor como contexto; no es lectura obligatoria para estudiantes.

**Video — "Big Data In 5 Minutes" (Simplilearn)**
- Buscar en YouTube: `"Big Data In 5 Minutes Simplilearn"`
- Duración: ~5 minutos. Visualiza las 5 V con ejemplos concretos de Amazon, Netflix y Twitter. El ritmo acelerado lo hace adecuado como introducción visual antes de la clase o como refuerzo recomendado a estudiantes.

---

### 6.2 OLTP vs. OLAP y Data Warehouse

**AWS — "OLAP vs. OLTP: What's the Difference?"**
- URL: https://aws.amazon.com/compare/the-difference-between-olap-and-oltp/
- Relevancia: comparación técnica detallada con ejemplos de casos de uso reales. Amazon Web Services es el proveedor de nube líder en Chile y la región; usar su documentación como referencia refuerza la conexión entre contenido académico y práctica profesional. La tabla comparativa de características es transferible directamente a la clase.

**Kimball Group — "The Data Warehouse Toolkit" (recursos gratuitos)**
- URL: https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/
- Relevancia: Ralph Kimball es el arquitecto intelectual del modelo dimensional (esquema estrella/copo de nieve) que es el estándar de diseño de Data Warehouses. El sitio ofrece capítulos de muestra y artículos gratuitos. El Capítulo 1 de "The Data Warehouse Toolkit" (3.ª ed.) es la referencia más citada en la industria sobre diseño de DW para análisis. La arquitectura en capas (Staging → DW → Data Marts) corresponde exactamente al marco de Kimball.

**Microsoft — "What is a Data Warehouse?" (Azure documentation)**
- URL: https://learn.microsoft.com/en-us/azure/architecture/data-guide/relational-data/data-warehousing
- Relevancia: documentación oficial de Azure Synapse Analytics, el DW en la nube de Microsoft. Relevante porque los estudiantes con experiencia en Power BI ya están en el ecosistema Microsoft; esta documentación muestra cómo el DW industrial es la extensión natural de lo que hacen en Power BI de escritorio.

**Video — "Data Warehouse vs. Data Lake vs. Data Lakehouse" (IBM Technology)**
- Buscar en YouTube: `"Data Warehouse vs Data Lake IBM Technology"`
- Duración: ~9 minutos. Contextualiza el DW en la arquitectura de datos moderna y adelanta los conceptos de Data Lake y Lakehouse que los estudiantes encontrarán en sus carreras. Apropiado para recomendar a estudiantes que quieran profundizar más allá del contenido de clase.

---

### 6.3 ETL: Extraer, Transformar, Cargar

**Talend — "What is ETL (Extract, Transform, Load)?"**
- URL: https://www.talend.com/resources/what-is-etl/
- Relevancia: Talend es uno de los proveedores de herramientas ETL más utilizados en la industria. Su guía introductoria cubre las tres fases con ejemplos de retail y e-commerce directamente aplicables al caso TechStyle. Muestra también la distinción entre ETL y ELT (Extraer-Cargar-Transformar), variante que los estudiantes pueden encontrar en contextos de Data Lake.

**dbt Labs — "What is a data transformation?"**
- URL: https://docs.getdbt.com/terms/data-transformation
- Relevancia: dbt (data build tool) es la herramienta de transformación de datos de código abierto que más ha crecido en adopción en los últimos cinco años. La documentación es pedagógicamente clara y usa SQL como lenguaje de transformación, conectando directamente con la Unidad 3 del curso. Útil para mostrar que el ETL tiene una implementación moderna con SQL puro, no solo con herramientas de arrastrar-y-soltar.

**Video — "ETL vs. ELT: What's the Difference?" (Fivetran)**
- Buscar en YouTube: `"ETL vs ELT Difference Fivetran"`
- Duración: ~5 minutos. Introduce la variante ELT (load primero, luego transform en el DW) que es el patrón dominante en arquitecturas de nube modernas. No es necesario profundizarlo en clase, pero ayuda al profesor a responder la pregunta "¿por qué no simplemente cargar todo y limpiar después?" que invariablemente surge.

**Apache Airflow — "What is a Data Pipeline?"**
- URL: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html
- Relevancia: Apache Airflow es el orquestador de pipelines de datos más utilizado en la industria para programar y monitorear procesos ETL. La documentación introductoria muestra cómo un proceso ETL se convierte en un pipeline automatizado y repetible, que es exactamente la respuesta a la pregunta "¿cómo se ejecuta el ETL automáticamente cada noche?".

---

### 6.4 Síntesis: El Flujo Completo y la Arquitectura Moderna de Datos

**a16z (Andreessen Horowitz) — "The Modern Data Stack"**
- URL: https://a16z.com (buscar "modern data stack" en el buscador del sitio)
- Relevancia: el ensayo de a16z sobre el "Modern Data Stack" (Fivetran + Snowflake + dbt + Looker) muestra cómo la arquitectura OLTP → ETL → DW → BI que se enseña en clase se implementa hoy en startups y empresas de crecimiento rápido. El paralelismo con TechStyle es directo. Adecuado para el profesor como contexto; accesible también para estudiantes con interés en tecnología.

**Snowflake — "What is a Data Lakehouse?"**
- URL: https://www.snowflake.com/guides/data-lakehouse
- Relevancia: Snowflake es el DW en la nube más relevante del momento en el mercado latinoamericano. La guía introductoria explica la convergencia entre Data Warehouse y Data Lake en el concepto de Lakehouse, que es la arquitectura que muchas empresas chilenas están adoptando. Útil para mostrar que los conceptos del curso son la base de las discusiones arquitecturales actuales en la industria.

**Video — "How Netflix Builds Fast Pipelines" (Engineering Netflix)**
- Buscar en YouTube: `"Netflix data engineering pipeline"`
- Relevancia: Netflix es un caso extremo de Big Data (todas las 5 V al máximo) y publica regularmente sobre su arquitectura de datos. Ver cómo una empresa de clase mundial implementa el flujo OLTP → ETL → DW → BI refuerza que los conceptos del curso no son académicos abstractos sino la base de las decisiones de ingeniería más complejas de la industria tecnológica global.

---

*Documento preparado para uso interno del equipo docente. No distribuir a estudiantes.*
