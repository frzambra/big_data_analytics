# Professor's Class Brief — W02
## Tipos de SI, CMI, Calidad de Datos y Ética
**Curso**: Big Data y Analytics · ICOM E015 · Universidad San Sebastián
**Unidad**: 1 — Sistemas de Información en el Contexto Empresarial
**Duración**: 1 hora 20 minutos (clase magistral)

---

## 1. Core Thesis

Si la semana anterior estableció *qué* es un Sistema de Información y *cómo* se estructura internamente, esta sesión responde a una pregunta de mayor complejidad estratégica: **¿cómo elige una organización el SI correcto para cada nivel, cómo alinea todos esos sistemas hacia un objetivo común, y qué ocurre cuando los datos que los alimentan son incorrectos o se usan de forma éticamente cuestionable?** La clase articula un argumento en tres capas: primero, que existen tipos específicos de SI diseñados para resolver problemas específicos en niveles organizacionales específicos (TPS, BI, DSS, CRM, EIS, ERP); segundo, que el Cuadro de Mando Integral es el dispositivo conceptual que permite conectar todos esos sistemas hacia la estrategia corporativa mediante KPIs medibles; y tercero, que la confiabilidad de ese dispositivo depende enteramente de la calidad de los datos que lo alimentan.

El caso de los bonos mal pagados en TechStyle —$2,3 millones asignados por rendimiento ficticio a causa de un campo `fecha_entrega` ambiguamente definido— opera como el núcleo dramático de la sesión. No es un accidente técnico: es la consecuencia lógica de construir un CMI sobre datos sin exactitud, completitud, consistencia ni oportunidad. Este caso eleva la discusión más allá de la taxonomía de sistemas y la lleva a un terreno donde los estudiantes deben entender que **la calidad de datos es una responsabilidad organizacional, no solo un problema técnico**, y que el analista de datos —rol al que estos estudiantes se aproximan— es el primer guardián de esa integridad. La clase cierra introduciendo la dimensión ética y legal, subrayando que el manejo de datos personales no es una decisión opcional sino un marco regulado por la Ley 19.628 y los principios de privacidad por diseño.

---

## 2. Narrative Roadmap

La sesión se organiza en cuatro fases que construyen un argumento acumulativo. Cada fase resuelve una pregunta y genera la siguiente.

### Fase 1 — Diferenciación: El SI Correcto para cada Problema (≈ 25 min)

La clase abre recuperando el marco de la sesión anterior (datos → información → decisión, tres niveles organizacionales) para plantear la nueva pregunta: si hay tres niveles, ¿qué sistema específico sirve a cada uno? Se introduce la taxonomía de tipos de SI (TPS, BI, DSS, CRM, EIS) y se deepens con dos conceptos adicionales de alta relevancia práctica: el **ERP** como sistema integrador que unifica módulos bajo una única base de datos, y el **DSS** como herramienta de simulación de escenarios que transforma datos históricos en proyecciones de decisión.

El punto pedagógico crítico de esta fase es la comparación TPS vs BI: no son sistemas alternativos sino eslabones de la misma cadena. El TPS opera en tiempo real con pocas filas; el BI opera sobre millones de filas históricas. Esta distinción es la base para entender el flujo de datos entre sistemas (ETL y Data Warehouse) que se verá en detalle en W03. El ejercicio de clasificación ("¿Qué SI necesita cada situación?") sirve como verificación activa de comprensión antes de avanzar.

### Fase 2 — Alineación Estratégica: El CMI como Brújula Organizacional (≈ 25 min)

Establecida la diversidad de tipos de SI, emerge una pregunta natural: ¿cómo sabe Roberto si todos esos sistemas están apuntando en la misma dirección estratégica? La respuesta es el **Cuadro de Mando Integral** (Kaplan y Norton, 1992). Esta fase profundiza en las cuatro perspectivas —Financiera, Cliente, Procesos Internos, Aprendizaje y Crecimiento— desarrollando cada una con su pregunta estratégica, sus KPIs típicos y su conexión con los actores de TechStyle.

El argumento más importante de esta fase es la causalidad entre perspectivas: la rentabilidad financiera (perspectiva superior) es consecuencia de la satisfacción del cliente, que es consecuencia de procesos eficientes, que son consecuencia de personas capacitadas (perspectiva base). Esta arquitectura causal implica que un CMI que solo mide la perspectiva financiera —como hacían las empresas antes de 1992— es ciego a las causas de sus propios problemas. El concepto de **KPI SMART** (Específico, Medible, Alcanzable, Relevante, Acotado en el tiempo) cierra esta fase dotando a los estudiantes de un criterio práctico para evaluar si un indicador es genuinamente útil o meramente decorativo.

### Fase 3 — El Eslabón Débil: Calidad de Datos y su Impacto en el CMI (≈ 20 min)

Esta es la fase de mayor impacto dramático. El caso de los bonos mal pagados en TechStyle actúa como bisagra: demuestra que el CMI más sofisticado es inútil —o activamente dañino— si los datos subyacentes no cumplen con las cuatro dimensiones de calidad (exactitud, completitud, consistencia, oportunidad). La auditoría del dataset `techstyle_orders.csv` traduce estas dimensiones abstractas a hallazgos cuantificados: 847 fechas de entrega imposibles, 53.400 filas sin región, cuatro variantes del mismo nombre de ciudad.

La fase se amplía con dos dimensiones adicionales —unicidad y validez— para mostrar que la calidad de datos excede la simple presencia o ausencia de valores y abarca las reglas de negocio que los datos deben respetar. Cierra con el concepto de **gobierno de datos** como solución organizacional: la calidad no puede depender de la buena voluntad individual sino de roles formalizados (Data Owner, Data Steward) y de un catálogo de datos que establezca definiciones oficiales de cada campo.

### Fase 4 — El Marco Ético y Legal (≈ 10 min)

La sesión cierra con la dimensión que con mayor frecuencia se omite en los cursos técnicos: el analista de datos opera dentro de un marco ético y legal que delimita qué puede hacer con los datos, independientemente de lo que sea técnicamente posible. Se presentan tres principios (transparencia, proporcionalidad, seguridad) y la Ley 19.628 chilena como marco regulatorio vigente. El dilema de geolocalización de clientes introduce el concepto de **privacidad por diseño**: la solución técnicamente menos invasiva que logra el mismo objetivo siempre es la opción preferida. La clase cierra posicionando al analista no solo como un procesador de datos sino como un **guardián de la integridad informacional** de la organización.

---

## 3. Key Visual Evidence

| Visual | Archivo | Argumento que ilustra |
|---|---|---|
| **Pirámide Organizacional de TechStyle** | `img/piramide_organizacional_techstyle.jpg` | Sitúa los tipos de SI en la jerarquía organizacional. Demuestra visualmente que no existe un SI universal: cada nivel requiere un sistema con características de tiempo, volumen y granularidad distintas. |
| **Mapa Estratégico de TechStyle** | `img/mapa_estrategico_cadena_casual.jpg` | Ilustra la causalidad entre las cuatro perspectivas del CMI. Prueba que la rentabilidad no es causa sino consecuencia: emerge del aprendizaje → procesos → satisfacción del cliente → resultados financieros. |
| **Diagrama de Flujo del SI** | `img/diagrama_flujo_informacion_techStyle.jpg` | Reutilizado de W01, pero ahora en el contexto del CMI: muestra que los KPIs estratégicos son el producto final de un flujo que comienza en los datos operativos del TPS. |

**Nota para el profesor**: el mapa estratégico es el visual más importante de esta sesión. Si el tiempo es escaso, es el único que no debe omitirse. La causalidad entre perspectivas es el argumento que distingue el CMI de un simple tablero de indicadores.

---

## 4. Discussion Benchmarks

**Pregunta 1 — Diferenciación conceptual** *(después de la taxonomía de SI)*
> "TechStyle usa un TPS, un CRM, un BI y un EIS. Si tuvieran que eliminar uno de estos sistemas por razones presupuestarias, ¿cuál eliminarían y por qué? ¿Cuál sería imposible de eliminar sin que el negocio colapse?"

Esta pregunta fuerza a los estudiantes a pensar en jerarquías de valor entre sistemas, no solo en sus definiciones. Anticipar: probablemente defenderán el TPS como irremplazable (sin él no hay operación), lo que abre la discusión sobre dependencias de datos.

**Pregunta 2 — Evaluación de KPIs** *(después del CMI y los criterios SMART)*
> "Roberto tiene el siguiente KPI en su dashboard: 'Satisfacción del cliente'. ¿Es este un buen KPI para el CMI? ¿Qué tendría que cambiarle para que cumpla los criterios SMART? ¿De qué sistema de TechStyle provendría el dato?"

Obliga a aplicar inmediatamente los criterios SMART y a trazar la cadena que va del KPI hasta su fuente de datos. Demuestra que definir un KPI es también definir un requisito sobre el sistema de datos que lo alimenta.

**Pregunta 3 — Análisis causal del caso de bonos** *(después del caso TechStyle)*
> "En el caso de los bonos mal pagados, se identificaron fallas en el TPS, en el BI y en el proceso de auditoría. Si tuvieran que implementar una sola medida para evitar que esto vuelva a ocurrir, ¿cuál sería y en qué punto del sistema la aplicarían?"

Desarrolla el pensamiento sistémico y el diseño de controles. No hay una respuesta única correcta; el debate entre validación en el TPS versus auditoría en el BI es pedagógicamente productivo.

**Pregunta 4 — Dilema ético** *(después del marco ético y legal)*
> "TechStyle descubre que puede predecir con 87% de precisión qué clientes van a cancelar su suscripción, usando datos de comportamiento de navegación que los clientes entregaron 'para mejorar la experiencia de compra'. ¿Pueden usar esos datos para una campaña de retención? ¿Dónde está el límite entre personalización y vigilancia?"

Introduce la tensión entre valor de negocio y privacidad del usuario. Conecta con el principio de proporcionalidad y con el concepto de finalidad declarada en la Ley 19.628.

**Pregunta 5 — Integración y proyección** *(al cierre)*
> "Si el gobierno de datos asigna a cada área de TechStyle la responsabilidad sobre sus propios datos, ¿quién debería ser el Data Owner del campo `fecha_entrega`? ¿Logística? ¿TI? ¿El cliente? ¿Y quién debería ser el Data Steward que valida la calidad día a día?"

Personaliza el concepto de gobierno de datos en el caso concreto de TechStyle y genera discusión sobre la intersección entre estructura organizacional y gestión de datos.

---

## 5. Essential Vocabulary

| Término | Definición operacional en el contexto del curso |
|---|---|
| **TPS** (Transaction Processing System) | Sistema que registra transacciones operativas en tiempo real. Genera los datos crudos que alimentan todos los demás sistemas. Sin TPS no hay cadena informacional. |
| **BI** (Business Intelligence) | Sistema que analiza datos históricos almacenados en un Data Warehouse para producir reportes y dashboards tácticos. Opera sobre millones de filas; solo lectura. |
| **DSS** (Decision Support System) | Sistema que apoya decisiones no estructuradas mediante simulación de escenarios con datos históricos y modelos proyectivos. Apoya la decisión; no la reemplaza. |
| **ERP** (Enterprise Resource Planning) | Plataforma que integra múltiples módulos de SI (ventas, inventario, RRHH, finanzas) bajo una única base de datos compartida, eliminando silos de información. |
| **CMI / Balanced Scorecard** | Marco estratégico (Kaplan y Norton, 1992) que traduce la estrategia en KPIs medibles organizados en cuatro perspectivas causalmente interrelacionadas. |
| **Perspectivas del CMI** | Las cuatro dimensiones del desempeño organizacional: Financiera (resultados), Cliente (percepción), Procesos Internos (eficiencia operativa), Aprendizaje y Crecimiento (capacidades). |
| **KPI SMART** | Indicador clave de desempeño que cumple cinco criterios: Específico, Medible, Alcanzable, Relevante y Acotado en el tiempo. Un KPI que no cumple estos criterios no es útil para la toma de decisiones. |
| **Calidad de Datos** | Conjunto de dimensiones que determinan si un dato es apto para su uso en la toma de decisiones: exactitud, completitud, consistencia, oportunidad, unicidad y validez. |
| **Gobierno de Datos** | Estructura organizacional de políticas, roles y procesos que garantiza la calidad, seguridad y uso adecuado de los datos. Incluye los roles de Data Owner y Data Steward. |
| **Privacidad por Diseño** | Principio que establece que la protección de datos personales debe incorporarse en el diseño del sistema desde el inicio, no añadirse como capa posterior. Favorece la solución menos invasiva que logra el mismo objetivo de negocio. |
| **Ley 19.628** | Marco legal chileno de protección de datos personales. Establece que los datos solo pueden usarse para el fin declarado al momento de su recopilación y otorga al titular derechos de acceso, modificación y eliminación. |

---

## Notas de Coordinación Docente

- **Conexión con W01**: esta clase presupone que los estudiantes comprenden la jerarquía dato–información–decisión y los 5 componentes del SI. Si el laboratorio W01 evidenció confusión en alguno de estos conceptos, conviene dedicar 5 minutos adicionales al repaso inicial antes de introducir la taxonomía de tipos de SI.
- **Conexión con W03**: el flujo ETL (Extracción, Transformación y Carga) y el Data Warehouse se mencionan tangencialmente en esta sesión como el mecanismo que conecta el TPS con el BI. Es intencional no profundizarlos aquí; la sesión W03 los desarrollará en detalle. No responder preguntas sobre ETL con más profundidad de la necesaria para no adelantar contenido.
- **Laboratorio W02**: el Lab conecta directamente con las fases 1 y 2 de esta clase. La Parte A (dashboards por nivel organizacional en Power BI) materializa la taxonomía de tipos de SI; la Parte B (auditoría de calidad en Power Query + diseño de CMI) materializa las fases 3 y parcialmente la 2. Los estudiantes ya tienen experiencia en Power BI y Power Query, por lo que el desafío del lab es conceptual, no técnico.

---

---

## 6. Online Reference Materials

Recursos organizados por los cuatro bloques temáticos de la sesión. Cada entrada incluye el propósito pedagógico específico para facilitar la preparación del profesor.

### 6.1 Tipos de Sistemas de Información (TPS, BI, DSS, CRM, EIS, ERP)

**Laudon & Laudon, *Management Information Systems* (14.ª ed.) — Capítulo 2 y Capítulo 11**
- URL companion: https://www.pearson.com (buscar ISBN 978-0134639710).
- El Capítulo 2 ("Global E-Business and Collaboration") detalla los tipos de SI por nivel organizacional. El Capítulo 11 ("Managing Knowledge and Artificial Intelligence") profundiza en DSS y sistemas de soporte a decisiones. Son las referencias académicas directas del contenido de la Fase 1.

**SAP Learning Hub — "What is an ERP System?"**
- URL: https://www.sap.com/insights/what-is-erp.html
- Relevancia: descripción del ERP desde el proveedor líder del mercado. Útil para mostrar cómo el concepto teórico se concreta en el software que los estudiantes encontrarán en empresas reales. SAP es el ERP más usado en Chile en empresas medianas y grandes.

**Salesforce — "What is CRM?"**
- URL: https://www.salesforce.com/crm/what-is-crm/
- Relevancia: explicación del CRM desde el proveedor más utilizado a nivel mundial. Incluye ejemplos de casos de uso que complementan el personaje de María en TechStyle. Recomendable también como lectura optativa para estudiantes.

**Video — "Business Intelligence vs. Data Analytics" (Alex The Analyst)**
- Buscar en YouTube: `"Business Intelligence vs Data Analytics Alex The Analyst"`.
- Duración: ~10 minutos. Clarifica la distinción entre BI (análisis de datos históricos para reportes tácticos) y analytics avanzado, anticipando la transición conceptual hacia W03.

---

### 6.2 Cuadro de Mando Integral (CMI / Balanced Scorecard)

**Artículo fundacional — Kaplan & Norton, "The Balanced Scorecard—Measures That Drive Performance" (HBR, 1992)**
- URL: https://hbr.org/1992/01/the-balanced-scorecard-measures-that-drive-performance
- Relevancia: el artículo original de 8 páginas publicado en Harvard Business Review. Lectura obligatoria para el profesor antes de impartir esta sección. El lenguaje es accesible y los ejemplos de empresas manufactureras son fácilmente trasladables al caso TechStyle. Disponible con suscripción institucional; la USS puede tener acceso vía biblioteca.

**Balanced Scorecard Institute — Recursos gratuitos**
- URL: https://balancedscorecard.org/resources/
- Relevancia: el instituto fundado por los colaboradores de Kaplan y Norton ofrece plantillas, guías y ejemplos de CMI en distintos sectores. La sección "BSC Basics" es ideal para preparar los ejemplos de la Fase 2. El mapa estratégico de ejemplo disponible en el sitio puede usarse como contraste con el mapa de TechStyle.

**Video — "Balanced Scorecard Explained" (Cascade Strategy)**
- Buscar en YouTube: `"Balanced Scorecard Explained Cascade Strategy"`.
- Duración: ~7 minutos. Visualización clara de las cuatro perspectivas con ejemplos empresariales modernos. Recomendable para proyectar como introducción antes de entrar al detalle de cada perspectiva.

**Harvard Business School — Online Case Studies on BSC**
- URL: https://www.hbs.edu/faculty/Pages/search.aspx (buscar "Balanced Scorecard Kaplan").
- Relevancia: Robert Kaplan publicó múltiples casos de aplicación del CMI en empresas reales. Aunque los casos completos son de pago, los abstracts y resúmenes ejecutivos son de acceso libre y sirven para preparar ejemplos adicionales al de TechStyle.

---

### 6.3 Calidad de Datos y Gobierno de Datos

**DAMA International — DAMA-DMBOK (Data Management Body of Knowledge)**
- URL: https://www.dama.org/cpages/body-of-knowledge
- Relevancia: el estándar internacional de gestión de datos. El Capítulo 13 ("Data Quality") define con precisión las dimensiones de calidad que se enseñan en la Fase 3. La versión completa es de pago, pero el sitio ofrece resúmenes y guías introductorias gratuitas. Es el marco que usan los profesionales de datos en Chile y el mundo.

**Gartner — "How to Build a Data Quality Strategy"**
- URL: https://www.gartner.com (buscar el título en la sección de investigación gratuita).
- Relevancia: fuente del dato citado en la clase ($12,9 millones de costo promedio anual por mala calidad de datos). El reporte completo es de pago, pero Gartner publica resúmenes ejecutivos gratuitos con las cifras clave. Útil para respaldar el argumento de costo ante estudiantes escépticos sobre la relevancia práctica de la calidad de datos.

**TDWI (Transforming Data with Intelligence) — "Data Quality Best Practices"**
- URL: https://tdwi.org (sección Research; buscar "Data Quality").
- Relevancia: TDWI es la asociación profesional de referencia en gestión de datos. Sus artículos de acceso libre explican las dimensiones de calidad con ejemplos de casos reales en retail y e-commerce, directamente transferibles al caso TechStyle.

**Video — "Data Governance Explained" (IBM Technology)**
- Buscar en YouTube: `"Data Governance Explained IBM Technology"`.
- Duración: ~8 minutos. Explica el gobierno de datos, los roles de Data Owner y Data Steward, y el catálogo de datos con claridad conceptual y ejemplos visuales. IBM Technology es un canal de referencia con alta calidad pedagógica.

---

### 6.4 Ética en Datos y Marco Legal Chileno

**Biblioteca del Congreso Nacional de Chile — Ley 19.628 (texto oficial vigente)**
- URL: https://www.bcn.cl/leychile/navegar?idNorma=141599
- Relevancia: texto legal completo y vigente. Para la clase es suficiente revisar los Artículos 4, 6, 9 y 20, que cubren el principio de finalidad, el consentimiento, los datos sensibles y los derechos del titular. El profesor debe conocer estos artículos para responder preguntas concretas durante la discusión ética.

**CNTV / Consejo para la Transparencia — Guía de Protección de Datos Personales (Chile)**
- URL: https://www.cplt.cl (sección Publicaciones; buscar "guía protección datos").
- Relevancia: el organismo regulador chileno publica guías prácticas sobre el cumplimiento de la Ley 19.628. Más accesible que el texto legal. Incluye ejemplos de sectores como retail y e-commerce que se alinean directamente con el caso TechStyle.

**GDPR.eu — "GDPR vs. Chilean Law 19.628: A Comparison"**
- URL: https://gdpr.eu (buscar "Chile" o "Latin America data protection" en el buscador del sitio).
- Relevancia: permite contextualizar la Ley 19.628 en el marco regulatorio global. La comparación con el GDPR europeo es relevante porque muchas empresas chilenas exportadoras (o que procesan datos de ciudadanos europeos) deben cumplir con ambas normativas.

**TED Talk — "Why Privacy Matters" (Glenn Greenwald, 2014)**
- URL: https://www.ted.com/talks/glenn_greenwald_why_privacy_matters
- Duración: 20 minutos.
- Relevancia: argumento filosófico y político sobre por qué la privacidad no es solo un requisito legal sino un derecho fundamental. Útil para elevar la discusión ética más allá del cumplimiento normativo y conectar con el principio de privacidad por diseño. Puede recomendarse como lectura optativa a estudiantes interesados en profundizar.

**Future of Privacy Forum — "Privacy by Design: The 7 Foundational Principles"**
- URL: https://fpf.org (buscar "Privacy by Design Ann Cavoukian").
- Relevancia: el documento original de Ann Cavoukian que establece los 7 principios de privacidad por diseño, concepto mencionado en la Fase 4 de la clase. Lectura técnica pero accesible; las dos primeras páginas son suficientes para dominar el concepto antes de clase.

---

*Documento preparado para uso interno del equipo docente. No distribuir a estudiantes.*
