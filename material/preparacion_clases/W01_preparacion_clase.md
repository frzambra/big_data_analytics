# Professor's Class Brief — W01
## Sistemas de Información en el Contexto Empresarial
**Curso**: Big Data y Analytics · ICOM E015 · Universidad San Sebastián
**Unidad**: 1 — Sistemas de Información en el Contexto Empresarial
**Duración**: 1 hora 20 minutos (clase magistral)

---

## 1. Core Thesis

Esta clase establece el argumento fundacional de todo el curso: **los datos por sí solos no tienen valor; su valor emerge cuando son procesados, contextualizados y comunicados para apoyar una decisión específica**. El problema central que la sesión aborda es la brecha que existe entre la abundancia de datos que una organización moderna genera y la capacidad real de sus actores para convertir esa materia prima en decisiones informadas. María González, gerente de marketing de TechStyle, encarna ese problema: tiene 450.000 filas de datos de ventas y un presupuesto de $15 millones de pesos que debe asignar en horas. Sin las herramientas conceptuales correctas, la abundancia de datos se convierte en parálisis, no en claridad.

El segundo argumento que la clase construye es que los Sistemas de Información no son simplemente software: son ecosistemas sociotécnicos compuestos por cinco componentes interdependientes (hardware, software, datos, personas y procesos) organizados para servir a distintos niveles de la jerarquía organizacional. Comprender esta arquitectura es condición previa para entender por qué una base de datos mal diseñada o un dato mal registrado por Sofía en el nivel operativo puede invalidar la decisión estratégica de Roberto tres niveles más arriba. Este es el hilo conductor del semestre: la calidad de la decisión es función de la calidad del sistema que la alimenta.

---

## 2. Narrative Roadmap

La sesión se articula en cuatro fases pedagógicas que deben mantenerse en secuencia para preservar la lógica argumentativa.

### Fase 1 — Gancho Situacional: El Problema de María (≈ 15 min)
La clase abre con un escenario realista e inmediato: son las 9:00 AM del lunes, hay una reunión de gerencia y María tiene 450.000 filas sin procesar. El objetivo de esta fase no es enseñar nada todavía; es generar la pregunta correcta en los estudiantes: *¿qué diferencia hay entre tener datos y tener información?* Este gancho conecta con la experiencia previa de los estudiantes en Excel y Power BI, validando ese conocimiento mientras señala su límite: manejar herramientas no es lo mismo que comprender el sistema que las alimenta.

### Fase 2 — Marco Conceptual: La Jerarquía y el SI (≈ 30 min)
Una vez planteada la pregunta, la clase construye el andamiaje conceptual en dos movimientos:
- **La jerarquía dato–información–conocimiento–decisión**: usando el caso de María como hilo conductor, cada nivel de la jerarquía se ilustra con un ejemplo concreto extraído del dataset de TechStyle. El ejercicio de clasificación ("¿dato, información o conocimiento?") funciona como verificación de comprensión en tiempo real.
- **El SI y sus 5 componentes**: se introduce la definición formal del SI (Laudon & Laudon) y se operacionaliza inmediatamente a través del modelo IPO aplicado al sistema de pedidos de TechStyle. La actividad en parejas del sistema bancario ancla los conceptos en la experiencia personal de los estudiantes.

### Fase 3 — Niveles Organizacionales y Flujo de Valor (≈ 25 min)
Esta es la fase de mayor densidad conceptual. Se introduce la pirámide organizacional con sus tres niveles (operativo, táctico, estratégico) personificados en Sofía, Juan/María y Roberto. El argumento central es que el **mismo dato** produce valor diferente dependiendo del nivel que lo consume. La tabla "Decisiones según el Nivel" y el ejercicio de trazabilidad del pedido #8821 desde la tablet de Sofía hasta el dashboard de Roberto demuestran que el SI es una cadena de valor informacional: su resistencia está determinada por su eslabón más débil.

### Fase 4 — Proyección y Cierre (≈ 10 min)
La clase cierra retornando a María: ahora los estudiantes tienen el vocabulario para entender por qué ella necesita algo más que una tabla dinámica. Se mencionan las tendencias actuales (cloud, APIs, Big Data) para situar el curso en el ecosistema tecnológico contemporáneo, y se presenta el laboratorio W01 como la materialización práctica de todo lo discutido: de dato crudo a recomendación ejecutiva en 30 minutos.

---

## 3. Key Visual Evidence

La sesión hace uso de cuatro recursos visuales con funciones pedagógicas distintas. El profesor debe conocer el argumento que cada uno ilustra, no solo su apariencia.

| Visual | Archivo | Argumento que ilustra |
|---|---|---|
| **Diagrama Jerarquía del Dato** | `img/diagrama_jerarquia_dato.png` | Muestra la transformación secuencial de datos en decisiones. Prueba que los SI automatizan ese recorrido; sin SI, el proceso es lento, costoso y propenso a errores humanos. |
| **Pirámide de Jerarquía – Visualización** | `img/jerarquia_dato_visualizacion.jpg` | Ilustra la proporción inversa: los datos son abundantes en la base, pero solo una fracción asciende hasta convertirse en decisión. El área de la pirámide es una metáfora del trabajo del analista: comprimir sin perder valor. |
| **Diagrama de Flujo del SI de TechStyle** | `img/diagrama_flujo_informacion_techStyle.jpg` | Operacionaliza el modelo IPO (Entrada → Proceso → Salida → Retroalimentación). Demuestra que el SI es cíclico: las decisiones generan nuevas operaciones que generan nuevos datos. |
| **Pirámide Organizacional de TechStyle** | `img/piramide_organizacional_techstyle.jpg` | Mapea los tres niveles organizacionales con sus actores específicos. Prueba que la granularidad y el horizonte temporal de la información varían según el nivel: Sofía necesita el pedido de hoy, Roberto necesita la tendencia de los próximos tres años. |

**Nota para el profesor**: si alguna imagen no carga correctamente en la presentación, los argumentos pueden sostenerse con las tablas y ejemplos textuales. Los visuales refuerzan, pero no son el único vehículo del argumento.

---

## 4. Discussion Benchmarks

Las siguientes preguntas están diseñadas para activar distintos niveles de pensamiento crítico (análisis, evaluación, síntesis) y pueden insertarse en los momentos de "Verificación" de cada sección.

**Pregunta 1 — Comprensión crítica** *(después de la jerarquía)*
> "María tiene las 450.000 filas en Excel. ¿En qué punto exacto del proceso deja de trabajar con datos y comienza a trabajar con información? ¿Existe ese punto de quiebre o es un continuo?"

Esta pregunta fuerza a los estudiantes a operacionalizar la distinción teórica y a reconocer que la frontera entre dato e información depende del propósito y el contexto.

**Pregunta 2 — Análisis sistémico** *(después de los 5 componentes)*
> "Cuando el sistema bancario te muestra tu saldo en la app, ¿cuál de los 5 componentes es el más crítico para la confianza del usuario? ¿Cambiaría tu respuesta si el banco fuera una fintech versus un banco tradicional?"

Obliga a pensar en interdependencias y en cómo el contexto de negocio redefine la jerarquía de los componentes.

**Pregunta 3 — Pensamiento causal** *(después de "¿Cuándo falla el SI?")*
> "En el escenario donde Sofía registra 'entregado' antes de entregar efectivamente el pedido, ¿el fallo es del componente 'personas', del componente 'procesos' o de ambos? ¿Qué cambio en el sistema —técnico u organizacional— podría prevenir este comportamiento?"

Desafía la visión simplista de que los fallos tecnológicos tienen causas técnicas, e introduce la noción de diseño de procesos como control.

**Pregunta 4 — Evaluación estratégica** *(después de los niveles organizacionales)*
> "Si Roberto toma una decisión de expansión basada en datos que Sofía registró incorrectamente hace tres meses, ¿de quién es la responsabilidad? ¿Del sistema, de Sofía, de Roberto, o del diseñador del SI?"

Esta pregunta abre la puerta a los temas de gobernanza, auditoría y calidad de datos que se desarrollarán en W02.

**Pregunta 5 — Síntesis y proyección** *(al cierre)*
> "¿En qué momento de su carrera profesional creen que van a ser Sofía, Juan o Roberto? ¿Y qué tipo de información van a necesitar de sus analistas de datos para tomar buenas decisiones?"

Personaliza el marco teórico y conecta el contenido con la identidad profesional de los estudiantes, que son administradores de empresas en formación.

---

## 5. Essential Vocabulary

Los siguientes términos constituyen el capital conceptual mínimo que el estudiante debe haber incorporado al término de la sesión. Se recomienda al profesor hacer una verificación informal al cierre preguntando por definiciones o ejemplos de 2–3 términos al azar.

| Término | Definición operacional en el contexto del curso |
|---|---|
| **Dato** | Hecho crudo, sin contexto ni propósito asignado. Por sí solo no permite tomar una decisión. Ej: `{región: RM, monto: 45000}`. |
| **Información** | Dato procesado y contextualizado que reduce la incertidumbre del tomador de decisiones. Ej: "Calzado generó el 54% de los ingresos en Q1". |
| **Conocimiento** | Patrones persistentes derivados de información acumulada. Permite anticipar comportamientos futuros. Ej: "Calzado crece sostenidamente en Q1 cada año". |
| **Sistema de Información (SI)** | Conjunto interrelacionado de hardware, software, datos, personas y procesos que transforma datos en información para apoyar decisiones organizacionales. |
| **Modelo IPO** | Input–Process–Output: marco conceptual que describe el ciclo funcional de cualquier SI. Incluye la retroalimentación como cuarto elemento. |
| **Nivel Operativo** | Nivel organizacional donde se ejecutan las transacciones diarias. Horizonte temporal: hoy. Necesidad informacional: granular y en tiempo real. |
| **Nivel Táctico** | Nivel organizacional donde se gestionan recursos y se evalúa el desempeño. Horizonte temporal: semana/mes. Necesidad informacional: agregada y comparativa. |
| **Nivel Estratégico** | Nivel organizacional donde se toman decisiones de largo plazo sobre dirección del negocio. Horizonte temporal: año/años. Necesidad informacional: sintética y proyectiva. |
| **Cadena de valor informacional** | Secuencia que une el dato registrado en el nivel operativo con la decisión tomada en el nivel estratégico. La calidad de la decisión final depende de la integridad de cada eslabón. |
| **Componentes del SI** | Los cinco elementos interdependientes: hardware, software, datos, personas y procesos. El fallo de cualquiera compromete la función completa del sistema. |

---

*Documento preparado para uso interno del equipo docente. No distribuir a estudiantes.*
