# Professor's Class Brief — W04
## De la Planilla al Modelo: Entidades, Relaciones y Normalización
**Curso**: Big Data y Analytics · ICOM E015 · Universidad San Sebastián
**Unidad**: 2 — Modelamiento y Gestión de Bases de Datos Relacionales
**Duración**: 1 hora 20 minutos (clase magistral)

---

## 1. Core Thesis

Esta sesión inaugura la Unidad 2 con un argumento central que debe quedar instalado desde los primeros minutos: **pasar de una planilla Excel a una base de datos relacional no es un cambio de herramienta, es un cambio de representación de la realidad**. Excel aplana la realidad organizacional en una sola tabla; el modelo relacional la articula según cómo las cosas realmente se relacionan en el negocio. Esta distinción no es estética: tiene consecuencias directas sobre la confiabilidad de los datos que, en última instancia, alimentan el CMI de Roberto.

El argumento se construye en dos movimientos encadenados. El primero demuestra que las planillas planas generan tres tipos de anomalías —actualización, inserción y eliminación— que no son errores del usuario sino fallas estructurales del modelo. Juan puede ser el analista más cuidadoso del mundo: si el modelo es plano, eventualmente habrá datos inconsistentes. El segundo movimiento introduce el remedio: el Modelo Entidad-Relación (MER) como lenguaje para describir la realidad del negocio antes de construir la base de datos, y la normalización (1FN → 2FN → 3FN) como el proceso disciplinado que elimina redundancias y dependencias inadecuadas hasta garantizar que cada hecho del negocio existe en exactamente un lugar del sistema.

La conexión con la decisión gerencial es directa e ineludible: si el email de 500 clientes Premium está desactualizado en la planilla plana de TechStyle porque nadie actualizó todas las filas, la campaña de María se dirige al segmento equivocado. Si el precio de un producto aparece con valores distintos en 1.200 filas —porque nadie actualizó todas cuando cambió— el reporte de margen de Juan es incorrecto. Un modelo en 3FN garantiza que ninguno de estos escenarios es posible por diseño, no por disciplina individual.

---

## 2. Narrative Roadmap

La sesión se articula en cuatro fases pedagógicas que deben mantenerse en secuencia. La lógica es acumulativa: cada fase genera el problema que la siguiente resuelve.

### Fase 1 — El Problema: La Planilla Imposible de TechStyle (≈ 15 min)

La clase abre con un escenario concreto: María abre `ventas_historial.xlsx` y encuentra 340.000 filas con toda la información de clientes, productos y ventas mezclada en una sola hoja. El objetivo de esta fase no es presentar soluciones todavía; es instalar tres anomalías como problemas genuinos que los estudiantes reconozcan como propios de su experiencia con Excel.

La **anomalía de actualización** se presenta con el ejemplo más intuitivo: si Juan Pérez cambia su email y aparece en 1.200 filas, actualizar correctamente todas las ocurrencias es una obligación manual que nadie puede garantizar. Un solo olvido produce un sistema con dos versiones del mismo cliente. La **anomalía de inserción** se plantea como pregunta directa: ¿cómo se registra un producto nuevo si todavía no tiene ninguna venta? En una planilla plana, la única opción es una fila con NULLs en las columnas de venta —una fila sin sentido analítico. La **anomalía de eliminación** es la más dramática: si se eliminan todas las ventas de un cliente porque son erróneas, el cliente desaparece del sistema junto con sus datos de contacto, región y segmento.

El punto pedagógico crítico de esta fase es que estas anomalías no son accidentes evitables: son consecuencias lógicas del diseño de planilla plana. La solución no es ser más cuidadoso; es cambiar el modelo.

### Fase 2 — El Marco Conceptual: Entidades, Atributos y Relaciones (≈ 30 min)

Una vez instalado el problema, la sesión introduce el vocabulario del MER como respuesta estructural. El argumento de apertura es filosófico antes de ser técnico: en el mundo real, un cliente existe independientemente de sus compras; un producto existe independientemente de quién lo compró. Una base de datos bien diseñada debe reflejar esa independencia ontológica, no colapsarla en una sola fila.

El concepto de **entidad** se introduce con la regla práctica del "¿hay más de uno de esto?": si la respuesta es sí y cada instancia necesita ser identificada y gestionada por separado, es una entidad. El concepto de **atributo** se conecta inmediatamente con los tipos de datos SQL (`INT`, `VARCHAR`, `DECIMAL`, `DATE`), preparando el terreno para el Diccionario de Datos. El concepto de **clave primaria (PK)** —atributo que identifica unívocamente cada fila— y de **clave foránea (FK)** —atributo que referencia la PK de otra tabla— son los mecanismos concretos que implementan las relaciones en SQL. El profesor debe insistir en que la FK no es solo una columna numérica: es una restricción de integridad que el motor de base de datos hace cumplir automáticamente, garantizando que no pueden existir ventas de clientes inexistentes.

Las **relaciones y su cardinalidad** (1:1, 1:N, N:M) se presentan con ejemplos del negocio TechStyle. El caso de la relación N:M entre Ventas y Productos es el más importante: demuestra por qué existe la tabla `DETALLE_VENTA` y por qué su clave primaria es compuesta. Si los estudiantes entienden este punto, han comprendido la lógica central del modelo relacional.

La introducción al **Diagrama de Casos de Uso UML** debe mantenerse breve en esta sesión (8–10 minutos). Su función es mostrar quién interactúa con el sistema (actores) y qué puede hacer (casos de uso) antes de diseñar las tablas. No es el foco de W04; se desarrollará más en W05 en el contexto de la implementación en MySQL.

### Fase 3 — La Normalización: 1FN → 2FN → 3FN (≈ 25 min)

Esta fase debe tratarse como un viaje con tres paradas, no como tres definiciones separadas. El caso de la Factura de TechStyle opera como hilo conductor: la misma tabla se transforma progresivamente hasta quedar en 3FN, permitiendo a los estudiantes ver el antes y el después de cada transformación.

**Primera Forma Normal (1FN)**: el punto de partida es la tabla de facturas con columnas `Item1_Cod, Item1_Nombre, Item2_Cod, Item2_Nombre`... El problema es inmediato: ¿qué pasa si un cliente compra 5 ítems? La estructura de la tabla tendría que cambiar. La solución es una fila por ítem, con clave primaria compuesta `(N_Factura, Cod_Prod)`. El nuevo problema que genera es menos obvio para los estudiantes: `Nombre_Prod` y `Precio` dependen solo de `Cod_Prod`, no del par completo. Este es el gancho para la 2FN.

**Segunda Forma Normal (2FN)**: la dependencia parcial (`Nombre_Prod` depende de solo *parte* de la clave compuesta) se identifica con la pregunta: "¿Cambiaría `Nombre_Prod` si cambiara `N_Factura` manteniendo el mismo `Cod_Prod`?" Si la respuesta es no, hay dependencia parcial. La solución —separar PRODUCTO de DETALLE— genera el beneficio inmediato de que actualizar el precio de Nike Air Max requiere modificar exactamente una fila. El nuevo problema: `Nombre_Cliente` y `Ciudad` en la tabla FACTURA dependen de `RUT`, no de `N_Factura`. Este es el gancho para la 3FN.

**Tercera Forma Normal (3FN)**: la dependencia transitiva (`Ciudad` depende de `RUT`, que no es la PK de FACTURA) se identifica con la pregunta: "¿Cambiaría `Ciudad` si cambiara `N_Factura` pero el mismo cliente hiciera otra compra?" Si la respuesta es no, hay dependencia transitiva. La solución separa CLIENTE de FACTURA. El resultado final son cuatro tablas limpias donde cada hecho del negocio existe en un único lugar.

**El Diccionario de Datos** cierra esta fase como el puente entre el diagrama MER y la implementación SQL. No es un documento opcional: es el contrato entre el diseñador del modelo y el desarrollador que construirá la base de datos. Cada atributo necesita tipo SQL, restricciones y descripción. El ejercicio de completar el diccionario de PRODUCTOS y VENTAS en el Desafío Rápido 3 prepara directamente el Lab W04.

### Fase 4 — Proyección: Del MER al SQL y Preview del Lab (≈ 10 min)

La sesión cierra demostrando que el MER en 3FN se traduce directamente a sentencias `CREATE TABLE`: cada entidad es una tabla, cada atributo es una columna con su tipo, cada PK y FK se declaran explícitamente. Los dos ejemplos de SQL (CLIENTE y FACTURA) no deben explicarse en detalle —eso es el lab— sino usarse para mostrar que el lenguaje formal del MER y el lenguaje del motor de base de datos son la misma lógica en distintas notaciones.

El preview del Lab W04 debe presentarse como la materialización completa de lo visto en clase: los estudiantes recibirán `techstyle_ventas_planas.csv`, identificarán las anomalías y violaciones de forma normal, diseñarán el diagrama MER en draw.io, completarán el diccionario de datos y escribirán las sentencias `CREATE TABLE`. El lab no introduce conceptos nuevos; los aplica todos.

---

## 3. Key Visual Evidence

| Visual | Recurso | Argumento que ilustra |
|---|---|---|
| **Tabla de la planilla plana de TechStyle** | Slide tabla (datos ficticios de Juan Pérez / Nike Air Max) | Demuestra visualmente que el mismo dato (cliente, producto) se repite en múltiples filas. Sin este contraste, las anomalías son abstractas. Con él, son inmediatamente reconocibles. |
| **Diagrama MER de TechStyle (Mermaid)** | Slide con bloque `{mermaid}` — 4 entidades: CLIENTE, PRODUCTO, VENTA, DETALLE_VENTA | Muestra la solución al problema de la planilla plana: cada entidad existe una sola vez, las relaciones son explícitas y tienen cardinalidad. Es el visual de mayor densidad conceptual de la sesión. |
| **Tabla: antes y después de cada FN** | Slides de normalización (tres tablas progresivas) | Hace visible la transformación: el estudiante puede comparar la tabla original con la tabla en 1FN y con la tabla en 2FN. Sin esta comparación, las formas normales parecen definiciones vacías. |
| **Diagrama MER del resultado de 3FN (Mermaid)** | Segundo bloque `{mermaid}` — 4 entidades: CLIENTE, FACTURA, PRODUCTO, DETALLE | Cierra el ciclo: el resultado final de normalizar la factura produce exactamente el mismo tipo de diagrama que se usó para modelar TechStyle desde el principio. Las dos partes de la clase se fusionan. |

**Nota para el profesor**: los dos diagramas Mermaid son los visuales más importantes de la sesión. Quarto los renderiza automáticamente en formato interactivo cuando se usa `{mermaid}`. Si el entorno no soporta Mermaid, las tablas de texto que describen entidades y atributos son suficientes para sostener el argumento; los diagramas refuerzan pero no son el único vehículo de la lógica.

---

## 4. Discussion Benchmarks

Las siguientes preguntas están diseñadas para activar análisis aplicado en los momentos de "Desafío Rápido" de la presentación. Cada una incluye la respuesta de referencia que el profesor debe tener preparada para guiar la discusión si los estudiantes no llegan al argumento central por sí mismos.

**Pregunta 1 — Diagnóstico de anomalías** *(después de la planilla plana)*
> "TechStyle tiene 180.000 filas en `ventas_historial.xlsx`. El analista detecta que el producto 'Nike Air Max' aparece con precio $89.990 en 1.100 filas y con precio $94.990 en 100 filas. ¿Qué anomalía es esta? ¿Cuál es el precio real del producto? ¿Cómo lo sabría sin llamar al área de Productos?"

Esta pregunta demuestra que las anomalías de actualización no solo son un problema de consistencia: producen incertidumbre analítica real que ninguna herramienta de BI puede resolver sin acceso a la fuente de verdad.

**Respuesta de referencia:**
- **Tipo de anomalía**: anomalía de actualización. Cuando el precio de Nike Air Max cambió (probablemente de $89.990 a $94.990 o viceversa), la actualización no se propagó a todas las filas donde el producto aparece. El resultado son dos versiones del mismo hecho en el sistema.
- **¿Cuál es el precio real?** Es imposible saberlo solo desde la planilla. $89.990 podría ser el precio histórico correcto para ventas anteriores al cambio, y $94.990 el precio actual; o podría ser que alguien actualizó 100 filas de las 1.200 y se olvidó del resto. Sin una fuente de verdad única (una tabla PRODUCTO con una sola fila para Nike Air Max), no hay forma de determinarlo desde el dato mismo.
- **Implicación analítica**: si Juan calcula el margen de Nike Air Max usando el campo `precio` de la planilla, su cálculo tomará el promedio de dos precios distintos que representan eventos distintos (o errores) — el resultado será incorrecto de formas que no son detectables desde el reporte.
- **La solución del modelo relacional**: en una tabla PRODUCTO normalizada, Nike Air Max tiene exactamente una fila con exactamente un precio. Si el precio cambia, se actualiza una fila. El dato es consistente en toda la base de datos automáticamente.
- **Punto de debate productivo**: ¿qué pasa si realmente queremos conservar el precio histórico al que se realizó cada venta? La respuesta conecta directamente con el diseño de `DETALLE_VENTA`: el `precio_unitario` debe guardarse en la línea de detalle de cada venta (precio al momento de la transacción) y el `precio_venta` en PRODUCTO debe reflejar el precio vigente hoy. Esto no es redundancia: son dos hechos de negocio distintos.

---

**Pregunta 2 — Identificación de entidades y relaciones** *(después del MER de TechStyle)*
> "TechStyle está evaluando agregar un módulo de devoluciones. Un cliente puede devolver uno o más productos de una venta. La devolución genera una nota de crédito por el monto devuelto. ¿Qué nuevas entidades agregarías al modelo? ¿Cómo se relacionan con VENTA y CLIENTE? ¿Cuál sería la clave primaria de cada nueva entidad?"

Obliga a aplicar las reglas de identificación de entidades a un contexto de extensión del modelo existente, y a pensar en relaciones antes de pensar en atributos.

**Respuesta de referencia:**
- **Entidades nuevas**: DEVOLUCION (cabecera de la devolución) y DETALLE_DEVOLUCION (líneas de productos devueltos). Opcionalmente, NOTA_CREDITO si tiene atributos propios más allá del monto.
- **Relaciones**:
  - `VENTA (1) → DEVOLUCION (N)`: una venta puede originar múltiples devoluciones parciales, pero cada devolución pertenece a exactamente una venta. Cardinalidad 1:N.
  - `CLIENTE (1) → DEVOLUCION (N)`: por conveniencia, se puede referenciar directamente al cliente, aunque también se puede derivar a través de VENTA. Depende de si el cliente puede devolver sin la venta original (ej.: perdió el comprobante). Esta es una decisión de negocio, no técnica.
  - `DEVOLUCION (1) → DETALLE_DEVOLUCION (N)` y `PRODUCTO (1) → DETALLE_DEVOLUCION (N)`: mismo patrón que VENTA → DETALLE_VENTA. La tabla intermedia es necesaria para la relación N:M implícita entre devoluciones y productos.
- **Claves primarias**: `DEVOLUCION.devolucion_id` (INT, autogenerado). `DETALLE_DEVOLUCION` tendrá PK compuesta `(devolucion_id, producto_id)`.
- **Atributo clave en DETALLE_DEVOLUCION**: `cantidad_devuelta` y `motivo_devolucion` (VARCHAR). El precio de devolución puede vincularse al `precio_unitario` de la línea de DETALLE_VENTA original.
- **Punto de debate productivo**: ¿NOTA_CREDITO es una entidad separada o un atributo de DEVOLUCION? Si la nota de crédito tiene fecha de emisión, número de documento, y puede aplicarse a compras futuras → es una entidad. Si solo es el monto total de la devolución → es un atributo calculado. Esta distinción (¿tiene identidad propia en el negocio o es solo una propiedad de otra cosa?) es la misma regla de identificación de entidades que se aplica siempre.

---

**Pregunta 3 — Diagnóstico de normalización** *(después de 1FN, 2FN, 3FN)*
> "La siguiente tabla del sistema de RRHH de TechStyle fue declarada en 1FN con clave primaria compuesta `(ID_Contrato, ID_Cargo)`. Columnas: `ID_Contrato, ID_Empleado, Nombre_Empleado, ID_Cargo, Nombre_Cargo, Sueldo_Base, ID_Departamento, Nombre_Depto`. ¿Viola la 2FN? ¿Viola la 3FN? ¿A cuántas tablas llegas en 3FN?"

Esta es la pregunta del Desafío Rápido 3 de la presentación. El valor pedagógico está en que combina ambas formas normales en un solo caso y obliga a identificar dos tipos de dependencias distintas simultáneamente.

**Respuesta de referencia:**
- **Violación de 2FN — Dependencias parciales** (respecto de la PK compuesta `(ID_Contrato, ID_Cargo)`):
  - `Nombre_Empleado` depende solo de `ID_Empleado`, que a su vez depende de `ID_Contrato`. Esto es indirecto: `Nombre_Empleado` no depende de `ID_Cargo` en absoluto.
  - `Nombre_Cargo` y `Sueldo_Base` dependen solo de `ID_Cargo`, no de `ID_Contrato`.
  - `ID_Departamento` podría depender de `ID_Cargo` (cada cargo pertenece a un departamento) → dependencia parcial respecto a la clave completa.
  - Resolución: separar CARGO `(ID_Cargo, Nombre_Cargo, Sueldo_Base, ID_Departamento)` del resto.
- **Violación de 3FN — Dependencias transitivas** (después de aplicar 2FN):
  - En la tabla resultante de CARGO: `Nombre_Depto` depende de `ID_Departamento`, que no es la PK de CARGO. `ID_Departamento → Nombre_Depto` es una dependencia transitiva vía un no-clave.
  - Resolución: separar DEPARTAMENTO `(ID_Departamento, Nombre_Depto)`.
  - En CONTRATO: `Nombre_Empleado` depende de `ID_Empleado`, no de `ID_Contrato`. Dependencia transitiva.
  - Resolución: separar EMPLEADO `(ID_Empleado, Nombre_Empleado)`.
- **Tablas en 3FN**:
  1. `CONTRATO (ID_Contrato, ID_Empleado FK, ID_Cargo FK)` — PK: ID_Contrato
  2. `EMPLEADO (ID_Empleado, Nombre_Empleado)` — PK: ID_Empleado
  3. `CARGO (ID_Cargo, Nombre_Cargo, Sueldo_Base, ID_Departamento FK)` — PK: ID_Cargo
  4. `DEPARTAMENTO (ID_Departamento, Nombre_Depto)` — PK: ID_Departamento
- **Observación pedagógica**: partimos de 1 tabla con 8 columnas y llegamos a 4 tablas. Esto parece "más complejo", pero cada tabla ahora tiene una única razón para cambiar. Si el sueldo de un cargo cambia → 1 fila en CARGO. Si un empleado cambia su nombre → 1 fila en EMPLEADO. Si un cargo cambia de departamento → 1 fila en CARGO. La aparente complejidad estructural es la fuente de la simplicidad operacional.

---

**Pregunta 4 — Diseño de PK y FK** *(después del slide "Del MER al SQL")*
> "El equipo de TI de TechStyle propone usar el RUT del cliente como clave primaria de la tabla CLIENTE en lugar de un `cliente_id` autogenerado. ¿Es una buena decisión? ¿Qué ventajas y riesgos tiene cada opción?"

Introduce el debate entre claves naturales (que tienen significado de negocio) y claves artificiales (autogeneradas sin significado), un dilema de diseño real que los estudiantes encontrarán en su práctica profesional.

**Respuesta de referencia:**
- **Argumento a favor del RUT como PK**: el RUT es único por naturaleza (el SII lo garantiza), ya existe en los sistemas de TechStyle, y hace que las consultas de búsqueda de un cliente específico sean directas (no necesitas conocer el `cliente_id` si tienes el RUT). Elimina la posibilidad de duplicar clientes: dos registros con el mismo RUT serían rechazados automáticamente por la constraint de PK.
- **Argumentos en contra del RUT como PK — los tres riesgos relevantes**:
  1. **Extranjeros**: TechStyle vende a turistas y residentes extranjeros que no tienen RUT chileno. Un sistema con RUT como PK obligatoria no puede registrarlos sin distorsionar el campo (RUT falsos, pasaportes, etc.).
  2. **Cambio de PK**: el RUT es relativamente estable, pero en casos de errores de registro o cambios legales puede necesitar modificarse. En un modelo relacional, cambiar la PK de CLIENTE requiere actualizar en cascada todas las FK que la referencian (VENTA, DETALLE_VENTA, etc.). Con un `cliente_id` autogenerado, el RUT es solo un atributo más — modificarlo no afecta ninguna FK.
  3. **Performance en JOINs masivos**: el RUT es un VARCHAR(12). Hacer JOINs entre millones de filas de VENTA y CLIENTE usando strings de 12 caracteres es más lento que usar INT. Para TechStyle con 340.000 pedidos diarios, esto tiene impacto medible.
- **La decisión práctica en la industria**: la práctica estándar es usar `cliente_id INT AUTO_INCREMENT` como PK (clave artificial) y declarar el RUT como `UNIQUE NOT NULL` (índice único, pero no PK). Así se capturan los beneficios del RUT sin sus riesgos: búsquedas por RUT son rápidas (por el índice único), los JOINs usan INT, y el sistema puede manejar clientes sin RUT declarando ese campo como nullable o utilizando un identificador alternativo.
- **Conexión con el diccionario de datos**: esta decisión debe documentarse explícitamente en el Diccionario de Datos de CLIENTE, con la justificación. Si el próximo desarrollador no sabe por qué existe `cliente_id` cuando ya existe el RUT, puede asumir que es un error y eliminarlo.

---

**Pregunta 5 — Síntesis y conexión estratégica** *(al cierre)*
> "Roberto acaba de presentar el CMI de TechStyle al directorio. El KPI 'Tasa de retención de clientes Premium' muestra 87%, pero el área de Marketing sospecha que el número es incorrecto porque hay clientes que cambiaron su segmento sin que el sistema lo registrara correctamente. ¿Es este un problema de KPI, de BI o de modelo de datos? ¿Qué debería revisar Juan antes de confirmar o desmentir el número?"

Conecta el contenido técnico de toda la sesión con el impacto estratégico en la toma de decisiones, cerrando el argumento central del curso: la calidad de la decisión es función de la calidad del modelo de datos que la alimenta.

**Respuesta de referencia:**
- **¿Es un problema de KPI, de BI o de modelo de datos?** De modelo de datos, y probablemente de proceso. El KPI (Tasa de retención de clientes Premium) está bien definido si cumple los criterios SMART. El BI (Power BI) calcula correctamente lo que le pidan. El problema está en cómo el sistema OLTP registra (o no registra) los cambios de segmento de los clientes a lo largo del tiempo.
- **El problema de fondo — ausencia de historial**: en un modelo simple, el atributo `segmento` de la tabla CLIENTE tiene un solo valor — el actual. Si el cliente pasa de Premium a Estándar, el UPDATE sobreescribe el valor previo. El sistema pierde la información histórica de cuándo el cliente era Premium. La tasa de retención calculada sobre ese campo refleja el estado actual, no el histórico.
- **Solución de modelo**: implementar una tabla `HISTORIAL_SEGMENTO (cliente_id FK, segmento, fecha_inicio, fecha_fin)` que registra cada cambio de segmento con fechas. La tasa de retención se calcularía sobre los clientes que tenían `segmento = 'Premium'` en `fecha_inicio` del período analizado, no sobre los que tienen `segmento = 'Premium'` hoy.
- **Qué debe revisar Juan antes de confirmar el número**:
  1. ¿Cómo se define operacionalmente "cliente Premium retenido"? ¿Sigue siendo Premium al final del período? ¿Hizo al menos una compra? (Definición de negocio — Diccionario de Datos)
  2. ¿La tabla CLIENTE conserva el historial de segmentos o solo el valor actual? (Diseño del modelo)
  3. ¿Qué consulta SQL genera el 87%? ¿Qué tabla consulta y en qué campo? (Auditoría de la fuente del KPI)
  4. Si el modelo no conserva historial, ¿hay alguna tabla de log o auditoría en el OLTP que registre los cambios? (Fuente alternativa)
- **Conclusión clave**: el 87% puede ser correcto o incorrecto, pero sin las respuestas anteriores no es posible determinarlo desde el BI. Este escenario ocurre cuando el modelo de datos se diseñó pensando en "cuál es el segmento actual del cliente" y no en "cuál ha sido la evolución del segmento del cliente en el tiempo". Es una decisión de diseño que debe tomarse en la fase de modelado, no puede corregirse en la capa de BI.

---

## 5. Essential Vocabulary

Los siguientes términos constituyen el capital conceptual mínimo que el estudiante debe haber incorporado al término de la sesión. Se recomienda verificar 3–4 términos al azar durante el cierre antes del preview del lab.

| Término | Definición operacional en el contexto del curso |
|---|---|
| **Entidad** | Objeto, persona o concepto del negocio que tiene existencia independiente y necesita ser almacenado. Se identifica porque puede haber más de uno y cada instancia debe ser distinguible de las demás. En TechStyle: CLIENTE, PRODUCTO, VENTA. |
| **Atributo** | Propiedad o característica de una entidad. Se convierte en una columna de la tabla SQL. Puede ser simple (nombre), compuesto (dirección = calle + número) o derivado (edad, calculable a partir de fecha_nacimiento). |
| **Clave Primaria (PK)** | Atributo o combinación de atributos que identifica unívocamente cada fila de una tabla. No puede repetirse ni contener valores nulos. Puede ser simple (un atributo) o compuesta (dos o más atributos). |
| **Clave Foránea (FK)** | Atributo en una tabla que referencia la clave primaria de otra tabla, estableciendo el vínculo entre entidades. El motor de base de datos garantiza integridad referencial: no puede existir una FK que referencie una PK inexistente. |
| **Relación** | Asociación entre dos entidades. Se clasifica por cardinalidad: 1:1, 1:N o N:M. Las relaciones N:M deben implementarse mediante una tabla intermedia con clave primaria compuesta. |
| **Cardinalidad** | Cuantificación de la relación entre entidades: cuántas instancias de una entidad pueden asociarse con instancias de la otra. Determina el diseño de las FK y las tablas intermedias. |
| **Modelo Entidad-Relación (MER)** | Representación gráfica de las entidades de un negocio, sus atributos y las relaciones entre ellas. Es el "plano" que guía la implementación de la base de datos, independiente del software específico que se use. |
| **Normalización** | Proceso de organización de un modelo relacional para eliminar redundancias y dependencias inadecuadas entre atributos, siguiendo una secuencia de formas normales. El objetivo es que cada hecho del negocio exista en exactamente un lugar del sistema. |
| **Primera Forma Normal (1FN)** | Una tabla está en 1FN si cada celda contiene un único valor atómico (indivisible) y no existen grupos de columnas repetidos. Requisito: definir una clave primaria que identifique unívocamente cada fila. |
| **Segunda Forma Normal (2FN)** | Una tabla está en 2FN si está en 1FN y cada atributo no-clave depende de la clave primaria completa (no de una parte de ella). Aplica solo cuando la clave primaria es compuesta. Elimina dependencias parciales. |
| **Tercera Forma Normal (3FN)** | Una tabla está en 3FN si está en 2FN y ningún atributo no-clave depende de otro atributo no-clave (no hay dependencias transitivas). Garantiza que cada atributo describe exclusivamente a su entidad y no a otra entidad que podría separarse. |
| **Diccionario de Datos** | Documento formal que especifica, para cada atributo de cada tabla, su nombre, tipo de dato SQL, restricciones (NOT NULL, UNIQUE, CHECK, DEFAULT) y descripción de negocio. Es el contrato entre el diseñador del modelo y el desarrollador que implementará la base de datos. |
| **Integridad Referencial** | Propiedad del sistema de base de datos que garantiza que todas las referencias FK apuntan a PK existentes. Impide la existencia de registros huérfanos (ventas de clientes inexistentes, detalles de ventas eliminadas). |
| **Anomalía de Actualización** | Error que ocurre en modelos no normalizados cuando un cambio en un dato requiere actualizar múltiples filas, y la actualización no es completa. Produce versiones contradictorias del mismo hecho en el sistema. |

---

## Notas de Coordinación Docente

- **Conexión con W03**: la Unidad 2 se presenta como la respuesta a la pregunta implícita de W03: "¿cómo se diseña el OLTP que alimenta el ETL y el DW que alimentan el CMI de Roberto?". Los estudiantes vieron el flujo completo en W03; ahora aprenden a diseñar su eslabón más importante. Si la Solemne 1 evidenció confusión sobre por qué el OLTP existe separado del DW, esta sesión refuerza ese argumento desde el diseño hacia abajo.
- **Conexión con W05**: en W05 se profundizará el Diagrama de Casos de Uso UML y el Modelo Relacional como traducción formal del MER. La introducción al UML en W04 debe quedar en el nivel de vocabulario básico (actores, casos de uso, relaciones); no profundizar en `<<include>>`, `<<extend>>` ni en diagramas de secuencia, que son contenido de W05.
- **Conexión con W06–W07**: la implementación en MySQL es la materialización de los modelos diseñados en W04–W05. El Diccionario de Datos completado en el Lab W04 será el insumo directo para las sentencias `CREATE TABLE` que los estudiantes ejecutarán en MySQL Workbench en W06. La coherencia entre ambas semanas es crítica: si el Diccionario de W04 tiene errores de tipo de dato, se arrastrarán a W06.
- **Perfil de estudiante**: los estudiantes ya conocen Power Query, Power Pivot y Power BI. Han trabajado con modelos estrella sin saber que se llaman así. Una estrategia pedagógica efectiva es reconocer ese conocimiento previo explícitamente: "el modelo que construyeron en draw.io hoy es la versión formalizada del modelo estrella que vieron en Power BI". La normalización hace que el modelo estrella sea correcto antes de implementarlo.
- **Errores frecuentes a anticipar**: (1) confundir PK con campo único — una PK es única y no nula, pero no todo campo único es PK; (2) olvidar la tabla intermedia en relaciones N:M, dibujando una línea directa entre dos entidades sin resolverla; (3) en la normalización, identificar dependencias transitivas solo como "A depende de B que depende de C" sin verificar que B no sea la PK — si B es la PK, no hay transitividad; (4) asumir que llegar a 3FN siempre requiere más tablas que en 2FN — a veces la misma tabla ya está en 3FN si sus dependencias transitivas son solo desde la PK.
- **Laboratorio W04**: el Lab materializa las cuatro fases de la clase en secuencia directa. La parte más compleja para los estudiantes suele ser la transición de "identificar la dependencia parcial" a "saber qué columnas mover a qué tabla nueva". Conviene adelantar en la última fase de la clase exactamente ese razonamiento con el caso de la factura: "si Nombre_Prod depende solo de Cod_Prod, todas las columnas que dependan solo de Cod_Prod van a la tabla PRODUCTO y se eliminan de DETALLE". El lab asume que ese razonamiento ya fue practicado.

---

## 6. Online Reference Materials

Recursos organizados por los cuatro bloques temáticos de la sesión.

### 6.1 Modelo Entidad-Relación (MER)

**Artículo fundacional — Peter Chen, "The Entity-Relationship Model — Toward a Unified View of Data" (1976)**
- Fuente: *ACM Transactions on Database Systems*, Vol. 1, No. 1.
- Cómo encontrarlo: buscar "Peter Chen Entity-Relationship Model 1976" en Google Scholar (scholar.google.com). Disponible en múltiples repositorios abiertos.
- Relevancia: el artículo original que introduce el modelo ER. No es necesario leerlo completo; las primeras 6 páginas establecen los conceptos de entidad, relación y atributo exactamente como se enseñan en el curso. Su lectura le permite al profesor contextualizar históricamente los conceptos: llevan más de 50 años siendo el estándar de diseño de bases de datos.

**Silberschatz, Korth & Sudarshan — *Database System Concepts* (7.ª ed.), Capítulo 6**
- URL companion: https://db-book.com (el sitio oficial del libro ofrece diapositivas y material de apoyo de acceso libre).
- Relevancia: el capítulo 6 ("Entity-Relationship Diagram") cubre entidades, atributos, relaciones, cardinalidad y la traducción del diagrama ER a tablas relacionales. Es el libro de referencia estándar para cursos de bases de datos a nivel universitario. El sitio db-book.com ofrece las slides del capítulo descargables en PDF.

**Lucidchart — "Entity-Relationship Diagram (ERD) Tutorial"**
- URL: https://www.lucidchart.com/pages/er-diagrams
- Relevancia: tutorial visual con ejemplos interactivos de diagramas ER. Incluye la notación crow's foot (pata de gallo) utilizada en el curso y ejemplos de situaciones de negocio similares a TechStyle. Útil para recomendar a estudiantes que necesiten refuerzo visual antes del Lab W04.

**Video — "Entity Relationship Diagram (ERD) Tutorial" (Lucidchart)**
- Buscar en YouTube: `"Entity Relationship Diagram ERD Tutorial Lucidchart"`.
- Duración: ~8 minutos. Demuestra paso a paso cómo construir un diagrama ER desde un caso de negocio, incluyendo la notación crow's foot. Recomendable para proyectar como referencia antes del segmento del lab sobre draw.io.

---

### 6.2 Normalización (1FN, 2FN, 3FN)

**E. F. Codd — "A Relational Model of Data for Large Shared Data Banks" (1970)**
- Fuente: *Communications of the ACM*, Vol. 13, No. 6.
- Cómo encontrarlo: buscar "Codd Relational Model 1970" en Google Scholar o en el ACM Digital Library (dl.acm.org).
- Relevancia: el artículo fundacional que introduce tanto el modelo relacional como los conceptos de normalización. Codd es al modelo relacional lo que Peter Chen es al MER. El profesor no necesita leerlo completo; las primeras 4 páginas contextualizan el argumento de por qué la normalización es necesaria. Útil para mencionar en clase que los conceptos tienen más de 50 años de respaldo científico.

**Khan Academy — "Normalization" (módulo de Bases de Datos)**
- URL: https://www.khanacademy.org (buscar "database normalization" en el buscador interno).
- Relevancia: explicación visual y accesible de 1FN, 2FN y 3FN con ejemplos interactivos. El nivel es apropiado para estudiantes que necesiten refuerzo adicional fuera de clase. La secuencia de ejemplos es similar a la del curso (tabla de facturas → normalización progresiva).

**Studytonight — "Database Normalization"**
- URL: https://www.studytonight.com/dbms/database-normalization.php
- Relevancia: explicación concisa de las tres formas normales con ejemplos visuales de tabla antes/después. Uno de los recursos en línea más consultados por estudiantes de bases de datos. Puede recomendarse como referencia rápida para el Lab W04.

**Video — "Database Normalization (1NF, 2NF, 3NF and BCNF) with Simple Example" (Decomplexify)**
- Buscar en YouTube: `"Database Normalization 1NF 2NF 3NF Decomplexify"`.
- Duración: ~26 minutos. Es el recurso en inglés más claro disponible sobre normalización, con el ejemplo progresivo de una tabla de ventas que se normaliza paso a paso. Apropiado para recomendar a estudiantes antes del Lab W04; el nivel de detalle cubre exactamente lo visto en W04.

---

### 6.3 Tipos de Datos SQL y Diccionario de Datos

**MySQL Reference Manual — "Data Types"**
- URL: https://dev.mysql.com/doc/refman/8.0/en/data-types.html
- Relevancia: la documentación oficial de MySQL sobre tipos de datos. Cubre `INT`, `VARCHAR`, `DECIMAL`, `DATE`, `BOOLEAN` y sus variantes con precisión. Es la fuente que los estudiantes usarán en W06–W07 cuando implementen en MySQL Workbench. Recomendable como referencia durante el Lab W04 para verificar la selección de tipos de datos.

**DAMA International — "Data Dictionary Best Practices" (resumen ejecutivo)**
- URL: https://www.dama.org (sección Resources; buscar "data dictionary" o "data catalog").
- Relevancia: DAMA es el organismo internacional de referencia en gestión de datos. Sus guías sobre diccionarios de datos definen el estándar profesional del documento que los estudiantes construirán en el Lab W04. El resumen ejecutivo gratuito es suficiente para preparar la explicación de para qué sirve el Diccionario y qué campos debe contener.

**Microsoft — "Database Design Basics"**
- URL: https://support.microsoft.com/en-us/office/database-design-basics-eb2159cf-1e30-401a-8084-bd4f9c9ca1f5
- Relevancia: tutorial de diseño de bases de datos escrito para un público de negocio, no técnico. Es útil porque usa el lenguaje de los estudiantes (viene del mundo de Excel y Access) para explicar por qué se necesita un modelo formal antes de construir una base de datos. Conecta el vocabulario previo de los estudiantes con el vocabulario del curso.

---

### 6.4 UML y Diagramas de Casos de Uso

**OMG — "Unified Modeling Language Specification" (resumen de casos de uso)**
- URL: https://www.omg.org/spec/UML/ (buscar "Use Case Diagram" en el documento de especificación).
- Relevancia: la especificación oficial del UML. Para el nivel de W04 es suficiente revisar la sección de Use Case Diagrams (actores, casos de uso, relaciones de asociación). No es necesario leer la especificación completa; las primeras páginas de la sección de casos de uso definen exactamente lo que se enseña.

**Lucidchart — "UML Use Case Diagram Tutorial"**
- URL: https://www.lucidchart.com/pages/uml-use-case-diagram
- Relevancia: tutorial visual sobre diagramas de casos de uso con ejemplos de sistemas similares a TechStyle (e-commerce, gestión de pedidos). Incluye la notación estándar (actores, elipses, líneas de asociación) y ejemplos de relaciones `<<include>>` y `<<extend>>` que se profundizarán en W05.

**Video — "Use Case Diagram Tutorial" (Lucidchart)**
- Buscar en YouTube: `"Use Case Diagram Tutorial Lucidchart"`.
- Duración: ~5 minutos. Introduce los elementos básicos del diagrama de casos de uso con ejemplos visuales. Apropiado como material de introducción antes de la sección de UML de la clase.

---

*Documento preparado para uso interno del equipo docente. No distribuir a estudiantes.*
