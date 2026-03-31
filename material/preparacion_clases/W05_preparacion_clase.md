# Professor's Class Brief — W05
## Del Modelo al Sistema: UML, Modelo Relacional Completo y MySQL Workbench
**Curso**: Big Data y Analytics · ICOM E015 · Universidad San Sebastián
**Unidad**: 2 — Modelamiento y Gestión de Bases de Datos Relacionales
**Duración**: 1 hora 20 minutos (clase magistral)

---

## 1. Core Thesis

Esta sesión completa el ciclo de diseño que comenzó en W04 y lo lleva hasta el umbral de la implementación. La tesis central es que **diseñar una base de datos sin antes entender quién usa el sistema y para qué produce modelos técnicamente correctos pero funcionalmente incompletos**. El modelo de W04 — cuatro tablas en 3FN — es un modelo limpio, pero incompleto para el negocio real de TechStyle. Las demandas concretas de María, Carlos y Roberto esta semana demuestran que la incompletitud no es un defecto de diseño sino una consecuencia de haber diseñado sin un mapa del sistema: el Diagrama de Casos de Uso UML.

El primer movimiento argumental establece que el Diagrama de Casos de Uso no es un formalismo burocrático: es la herramienta que responde tres preguntas que toda base de datos debe responder antes de que se cree la primera tabla. ¿Quiénes interactúan con el sistema? ¿Qué acciones realizan? ¿Qué información deben guardar esas acciones? Sin respuestas explícitas a estas preguntas, el diseñador crea las tablas que imagina que el sistema necesita, no las que el negocio realmente requiere. La demostración es directa: si en W04 se hubiera dibujado el diagrama de casos de uso completo de TechStyle, DESPACHO, DEVOLUCION y PROVEEDOR_PRODUCTO habrían aparecido en el modelo desde el primer día.

El segundo movimiento introduce el Modelo Relacional como la notación formal que convierte el diagrama MER en la especificación exacta de las tablas SQL. La notación `TABLA(`<u>`pk`</u>`, atributo, *fk*)` no es decorativa: es el lenguaje que el equipo de desarrollo leerá para construir el esquema. La distinción entre el MER (visual, orientado al negocio) y el Modelo Relacional (textual, orientado a la implementación) es el puente entre el análisis y la ingeniería.

El tercer movimiento amplía el modelo de TechStyle a nueve tablas mediante tres extensiones justificadas por casos de uso concretos: el módulo de proveedores (que introduce la relación N:M entre PROVEEDOR y PRODUCTO), el módulo de despacho (que introduce la relación 1:1 entre VENTA y DESPACHO como decisión de negocio, no técnica) y el módulo de devoluciones. El caso más pedagógicamente rico es CATEGORIA con su FK auto-referencial: es el primer ejemplo de que una tabla puede relacionarse consigo misma, y demuestra que el modelo relacional puede representar jerarquías arbitrariamente profundas sin cambiar la estructura.

El cierre en MySQL Workbench convierte el diseño en acción: el profesor demuestra que el EER Diagram de Workbench genera automáticamente el SQL correcto, incluyendo `AUTO_INCREMENT` en las PKs enteras y las cláusulas `ON DELETE`/`ON UPDATE` en las FKs. Estos dos elementos técnicos no son detalles de implementación: `AUTO_INCREMENT` es la respuesta al problema de los IDs duplicados en sistemas multiusuario, y las políticas de integridad referencial son decisiones de negocio que el motor de base de datos hace cumplir automáticamente.

---

## 2. Narrative Roadmap

La sesión tiene cuatro fases. Las dos primeras son conceptuales (UML y Modelo Relacional ampliado); las dos últimas son técnicas (MySQL Workbench e índices). El hilo conductor es siempre el mismo: cada decisión de diseño responde a una necesidad de negocio concreta de TechStyle.

### Fase 1 — De los Casos de Uso a las Entidades: el UML como Mapa del Sistema (≈ 20 min)

La clase abre con las tres demandas que Roberto recibe esta semana: María quiere datos de proveedores, Carlos quiere rastrear despachos, Roberto necesita registrar devoluciones. El movimiento pedagógico inicial consiste en demostrar que las tres demandas son nuevas entidades del sistema, no nuevos atributos de entidades existentes. Esto no es obvio para los estudiantes: el error frecuente es intentar agregar columnas a VENTA o PRODUCTO en vez de crear tablas nuevas.

El **Diagrama de Casos de Uso UML** se introduce como el instrumento que habría generado esas entidades en la fase de análisis, antes de diseñar tablas. Los cuatro elementos (actor, caso de uso, asociación, límite del sistema) deben presentarse con ejemplos del contexto TechStyle, no con definiciones abstractas. El punto más importante es la diferencia entre actor y entidad: un cliente es un actor porque interactúa con el sistema desde afuera; CLIENTE es una entidad porque el sistema guarda información sobre él. Estos conceptos no son idénticos: un Sistema de Pago Externo es actor (interactúa con TechStyle) pero no necesariamente genera una entidad propia si no se guardan datos sobre él.

La tabla "De los Casos de Uso a las Entidades" es el puente más importante de esta fase. Cada caso de uso que guarda o consulta información genera al menos una entidad. Este principio le da a los estudiantes un algoritmo de identificación de entidades más robusto que la regla del "¿hay más de uno de esto?" de W04: la regla de W04 es suficiente para entidades de negocio directas (clientes, productos), pero insuficiente para identificar entidades de proceso (despachos, devoluciones, movimientos de inventario), que solo aparecen cuando se analizan los casos de uso.

El Desafío Rápido 1 debe provocar el debate sobre si DEVOLUCION es una entidad nueva o un atributo de VENTA. El profesor debe conducir ese debate hacia el principio de identidad de negocio: si el evento tiene su propio ciclo de vida (estado: Pendiente → Aprobada → Rechazada), su propia fecha, sus propias relaciones con otras entidades y su propio conjunto de atributos que no dependen de la VENTA sino del evento de devolución en sí, entonces es una entidad. Este es el mismo criterio que diferencia VENTA de DETALLE_VENTA en el modelo de W04.

### Fase 2 — Ampliar el Modelo: Tres Módulos Nuevos y sus Decisiones de Diseño (≈ 25 min)

Esta fase construye el modelo completo de TechStyle en secuencia lógica, no como una lista de tablas nuevas sino como tres decisiones de diseño que cada una plantea un problema conceptual distinto.

**Módulo de Proveedores — La relación N:M entre PROVEEDOR y PRODUCTO**: el punto pedagógico es demostrar que la tabla `PROVEEDOR_PRODUCTO` no es una tabla "de relleno" creada para satisfacer la regla de normalización, sino la representación correcta de un hecho de negocio real: TechStyle negocia un precio distinto con cada proveedor para cada producto. El atributo `precio_compra` pertenece a la *relación* entre PROVEEDOR y PRODUCTO, no a ninguna de las dos entidades por separado. Si `precio_compra` estuviera en PRODUCTO, significaría que el producto tiene un único precio de compra independiente del proveedor — lo que es falso. Si estuviera en PROVEEDOR, significaría que el proveedor vende todo al mismo precio — igualmente falso. Solo en la tabla intermedia el precio de compra es un atributo correcto.

**Módulo de Despacho — La relación 1:1 como decisión de negocio**: el punto pedagógico es que la cardinalidad no es una propiedad matemática de las entidades sino una decisión sobre las reglas del negocio. En TechStyle, cada venta genera exactamente un despacho, porque así funciona la operación logística hoy. Si mañana el negocio permite despachos parciales (primero los ítems en stock, luego los que llegan en 48 horas), la relación cambia a 1:N con un campo `estado_despacho` y `fecha_despacho_parcial`. El modelo no cambia por razones técnicas; cambia cuando el negocio cambia. Esta distinción entre "lo que el modelo puede representar" y "lo que el negocio ha decidido" es crítica para que los estudiantes entiendan que el diseño de base de datos no es solo lógica sino también comprensión del negocio.

**Módulo de Categorías — La FK auto-referencial**: este es el caso más novedoso de la sesión. La tabla `CATEGORIA` con el atributo `categoria_padre_id FK → CATEGORIA` es el primer ejemplo de que una tabla puede relacionarse consigo misma. El profesor debe dibujar el ejemplo de manera concreta:

```
categoria_id | nombre_categoria | categoria_padre_id
      1      | Ropa             | NULL
      2      | Poleras          | 1
      3      | Pantalones       | 1
      4      | Poleras Manga Corta | 2
```

La jerarquía es arbitrariamente profunda sin cambiar el modelo. Esto conecta con el Desafío Rápido 2, cuyo valor pedagógico no es solo encontrar la solución sino reconocer el patrón: siempre que el negocio tenga una jerarquía padre-hijo (organigrama, categorías, árbol de cuentas contables, árbol geográfico de regiones/comunas), la FK auto-referencial es el patrón de implementación.

### Fase 3 — MySQL Workbench y la Implementación del Modelo (≈ 25 min)

Esta fase concreta el diseño en herramienta. El movimiento pedagógico es demostrar que el trabajo conceptual de las fases 1 y 2 no es burocrático: tiene consecuencias directas en el SQL que Workbench genera automáticamente.

**El EER Diagram de Workbench** se introduce con énfasis en tres funciones: crear tablas con tipos de dato precisos, conectar entidades con la herramienta de relaciones (que crea FK automáticamente con el nombre correcto), y usar Forward Engineering para generar el script DDL. El profesor debe realizar la demo en vivo con al menos dos tablas conectadas por una FK, mostrando que Workbench escribe el SQL que los estudiantes escribirían manualmente en W06.

**`AUTO_INCREMENT`** debe presentarse como la solución al problema de los IDs duplicados en sistemas multiusuario, no como una "opción cómoda". En TechStyle con 340.000 pedidos diarios, si dos usuarios insertan simultáneamente y ambos calculan manualmente que el siguiente `venta_id` disponible es 50.001, ambos crearían filas con la misma clave — violando la unicidad de la PK. `AUTO_INCREMENT` delega ese cálculo al motor de base de datos, que lo garantiza atómicamente. Esta es la conexión entre un detalle técnico y un requisito de negocio real.

**`ON DELETE` / `ON UPDATE`** son la parte conceptualmente más densa de esta fase. El profesor debe presentarlos como políticas de integridad referencial, no como opciones de configuración. Las cuatro opciones (`RESTRICT`, `CASCADE`, `SET NULL`, `NO ACTION`) tienen semántica de negocio distinta:
- `RESTRICT` en la FK de VENTA → CLIENTE: si alguien intenta borrar a Juan Pérez de la base de datos, MySQL lo impide porque existen ventas de Juan Pérez. Esto protege la integridad del historial de ventas.
- `CASCADE` en la FK de DETALLE_VENTA → VENTA: si se cancela y elimina una venta completa, todas sus líneas de detalle se eliminan automáticamente. Sin CASCADE, habría que borrar todas las líneas manualmente antes de borrar la venta — lo que en la práctica nadie haría, creando registros huérfanos.
- `SET NULL` se aplica a relaciones opcionales: si se da de baja un proveedor de PROVEEDOR_PRODUCTO, el campo `proveedor_id` en registros de despacho pendientes podría ponerse en NULL en vez de bloquearse — dependiendo de las reglas del negocio.

El Desafío Rápido 3 sobre el campo `estado` de DESPACHO (VARCHAR+CHECK vs. ENUM) es técnicamente correcto pero su valor pedagógico real es otro: obliga a los estudiantes a pensar en el costo de mantenimiento de las decisiones de tipo de dato. Si la lista de estados cambia en 6 meses, ¿cuál opción requiere menos trabajo? Esta es exactamente el tipo de pregunta que distingue a un analista de datos que diseña para el presente de uno que diseña para el ciclo de vida del sistema.

### Fase 4 — Índices: La Diferencia entre Segundos y Minutos (≈ 10 min)

La fase de cierre debe mantenerse breve y directamente conectada con el CMI de Roberto. El argumento es simple y contundente: un CMI que tarda 4 minutos en cargar no es un CMI funcional para la toma de decisiones. Los índices son uno de los principales mecanismos que previenen eso.

La analogía del índice de un libro es suficiente para el nivel conceptual de esta fase: sin índice, buscar "cliente_id = 84751" requiere leer todas las filas de la tabla; con índice, MySQL salta directamente al grupo de filas relevante. La PK siempre tiene índice automático. Las FKs tienen índice automático en Workbench. El profesor debe dar exactamente dos o tres ejemplos de índices adicionales justificados por patrones de consulta reales de TechStyle (María filtra por región y segmento; el CMI consulta ventas por fecha). No extender esta fase: el tema de optimización de consultas se profundizará en W09–W10.

---

## 3. Key Visual Evidence

| Visual | Recurso | Argumento que ilustra |
|---|---|---|
| **Diagrama de Casos de Uso de TechStyle** | Slide con bloque `{mermaid}` — 5 actores, 7 casos de uso | Demuestra que el sistema tiene más actores y funciones de las que el modelo de W04 representaba. Sin este visual, la necesidad de ampliar el modelo parece arbitraria; con él, cada nueva entidad tiene un caso de uso que la justifica. |
| **Tabla "De los Casos de Uso a las Entidades"** | Slide tabla (5 filas) | Es el puente algorítmico entre el análisis del sistema y el diseño del modelo. Los estudiantes pueden usarla como checklist en el Lab W05: cada caso de uso que guarda información debe tener su tabla. |
| **Diagrama MER del módulo de Proveedores (Mermaid erDiagram)** | Slide con bloque `{mermaid}` — 3 entidades | Demuestra que `precio_compra` pertenece a la relación N:M, no a ninguna de las dos entidades. Sin el diagrama, este argumento es abstracto; con él, la posición del atributo en `PROVEEDOR_PRODUCTO` es visualmente evidente. |
| **Tabla de ejemplo de FK auto-referencial en CATEGORIA** | Slide tabla (4 filas de datos concretos) | Hace tangible la jerarquía padre-hijo: los estudiantes ven que `categoria_padre_id = 2` en "Poleras Manga Corta" apunta a la fila con `categoria_id = 2`, que es "Poleras". Sin la tabla de datos, la FK auto-referencial es un concepto difícil de visualizar. |
| **Diagrama MER completo de TechStyle (Mermaid erDiagram, scrollable)** | Slide con 9 entidades y todas las relaciones | Es el artefacto de cierre conceptual de la fase 2: los estudiantes ven el sistema completo por primera vez. Debe tener `{.scrollable}` en el encabezado del slide para ser legible en pantalla. Es también el modelo que implementarán en el Lab W05. |
| **SQL generado por Workbench (dos tablas)** | Slide con código SQL — CLIENTES y VENTAS | Muestra que el trabajo conceptual de diseño se traduce directamente en SQL correcto, incluyendo `AUTO_INCREMENT`, `UNIQUE INDEX` en email, FK con `ON DELETE RESTRICT` y `ON UPDATE CASCADE`. Prepara el terreno para el Lab W05 sin enseñar SQL todavía. |

**Nota para el profesor**: el Diagrama MER completo con 9 entidades en Mermaid puede tardar varios segundos en renderizar en presentaciones Reveal.js. Se recomienda probar la renderización antes de la clase y, si el entorno tiene problemas, tener una imagen PNG exportada como respaldo. El argumento del diagrama no depende de la interactividad: una imagen estática sirve igual para ilustrar el modelo completo.

---

## 4. Discussion Benchmarks

**Pregunta 1 — Identificación de actores y entidades** *(después del Diagrama de Casos de Uso)*
> "TechStyle está evaluando integrar un sistema de reseñas: los clientes podrán calificar productos con 1 a 5 estrellas y dejar un comentario de texto. El sistema mostrará el promedio de calificaciones en la página del producto. ¿Qué actores participan en este caso de uso? ¿Genera nuevas entidades? Si es así, ¿cuáles y con qué atributos mínimos? ¿Cuál es la cardinalidad con CLIENTE y PRODUCTO?"

Esta pregunta obliga a aplicar el flujo completo: actor → caso de uso → entidad → atributos → relaciones, sin que la respuesta sea obvia desde el diagrama existente.

**Respuesta de referencia:**
- **Actores**: Cliente Web (genera la reseña), Sistema TechStyle (la almacena), Gerente de Marketing (la consulta para tomar decisiones de producto). Si se plantea moderación automática de contenido, también un servicio externo de análisis de texto.
- **Nueva entidad**: `RESENA (resena_id PK, cliente_id FK, producto_id FK, calificacion INT CHECK(calificacion BETWEEN 1 AND 5), comentario TEXT, fecha_resena DATE, estado VARCHAR CHECK IN ('Publicada', 'Pendiente', 'Rechazada'))`.
- **Relaciones**:
  - `CLIENTE (1) → RESENA (N)`: un cliente puede dejar muchas reseñas (de distintos productos). Pero en la mayoría de los sistemas, un cliente solo puede reseñar una vez cada producto → la PK compuesta `(cliente_id, producto_id)` puede reemplazar a `resena_id`, impidiendo duplicados automáticamente.
  - `PRODUCTO (1) → RESENA (N)`: un producto tiene muchas reseñas.
- **El promedio de calificaciones**: no es un atributo almacenado en PRODUCTO; es un atributo calculado (`SELECT AVG(calificacion) FROM RESENA WHERE producto_id = X`). Guardar el promedio en PRODUCTO crearía una dependencia funcional transitiva (el promedio depende de RESENA, no de PRODUCTO directamente) — violación de 3FN.
- **Punto de debate productivo**: ¿es RESENA una entidad débil (sin existencia independiente de PRODUCTO y CLIENTE) o una entidad fuerte? En términos estrictos, una reseña no tiene sentido sin el producto que reseña y el cliente que la escribe → es débil. Pero si TechStyle quiere moderar, auditar o usar el historial de reseñas, necesita que cada reseña tenga identidad propia con `resena_id`. La tensión entre entidad débil y fuerte es una decisión de diseño que depende del uso, no solo de la lógica de la entidad.

---

**Pregunta 2 — Cardinalidad como decisión de negocio** *(después del módulo de Despacho)*
> "Un nuevo stakeholder de TechStyle, Pedro (Gerente de Logística Regional), dice que en su región hay ventas que se despachan en dos envíos separados cuando el cliente pide productos de distintas bodegas. ¿Cómo afecta esto al diseño actual de la relación VENTA-DESPACHO? ¿Qué cambio específico en el modelo es necesario? ¿Qué consecuencias tiene ese cambio en las tablas existentes?"

Obliga a los estudiantes a ver que un cambio de cardinalidad no es un ajuste menor: tiene consecuencias en cascada sobre FKs, tablas y consultas.

**Respuesta de referencia:**
- **Impacto en la cardinalidad**: la relación pasa de 1:1 a 1:N. Una venta puede tener uno o más despachos. En el modelo actual, `venta_id` en DESPACHO es una FK con un índice que podría ser UNIQUE (porque se asumía 1:1). Si cambia a 1:N, ese constraint UNIQUE debe eliminarse.
- **Cambio en el modelo**:
  - Agregar `DESPACHO.numero_envio INT` para distinguir el primer envío del segundo dentro de la misma venta.
  - Agregar `DESPACHO.items_incluidos` o crear una tabla `DESPACHO_DETALLE (despacho_id FK, venta_id FK, producto_id FK, cantidad_despachada INT)` que especifique qué líneas de `DETALLE_VENTA` van en cada despacho.
- **Consecuencias en las consultas**: las consultas que calculaban "fecha de entrega de la venta" ahora deben agregar sobre múltiples despachos. Por ejemplo, para calcular el estado de entrega de una venta completa: `SELECT MIN(fecha_entrega_real) as primer_envio, MAX(fecha_entrega_real) as ultimo_envio FROM DESPACHO WHERE venta_id = X`. Si María quería saber "¿qué ventas del mes pasado se entregaron a tiempo?", la definición de "a tiempo" ahora es ambigua: ¿cuando llega el primer despacho? ¿cuando llega el último?
- **Punto clave para el profesor**: este escenario ilustra por qué las decisiones de cardinalidad no son inocentes. Cambiar de 1:1 a 1:N después de que el sistema está en producción requiere una migración de datos, cambios en consultas existentes y redefinición de KPIs que usaban la tabla DESPACHO. Costo de cambiar ahora: 1 hora de diseño. Costo de cambiar en producción: potencialmente semanas. Esta es la justificación real de por qué el análisis de casos de uso es obligatorio antes de diseñar.

---

**Pregunta 3 — ON DELETE / ON UPDATE como políticas de negocio** *(después del segmento de Workbench)*
> "El equipo de TI propone la siguiente política: si un cliente es dado de baja del sistema (eliminado de la tabla CLIENTES), todas sus ventas deben eliminarse automáticamente — para no dejar registros de ventas sin cliente asociado. ¿Cómo se implementaría esto en SQL? ¿Es una buena decisión de diseño? ¿Qué información se perdería? ¿Hay una alternativa mejor?"

Conecta el conocimiento técnico de ON DELETE con una decisión de negocio que tiene consecuencias sobre el análisis y la trazabilidad.

**Respuesta de referencia:**
- **Implementación SQL**: `FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id) ON DELETE CASCADE`. Esto hace que al eliminar un cliente, MySQL elimine automáticamente todas sus ventas, y en cascada todos los registros de `DETALLE_VENTA` que dependan de esas ventas.
- **¿Es una buena decisión?** En la inmensa mayoría de los contextos de negocio, no. Las razones:
  1. **Pérdida de historial financiero**: las ventas son registros contables. Eliminar ventas de un cliente que canceló su cuenta implica eliminar ingresos históricos del sistema. El balance contable cambia retroactivamente — lo que es incorrecto e inaceptable en cualquier sistema financiero.
  2. **Imposibilidad de análisis**: si TechStyle quiere analizar por qué los clientes que se dan de baja compraron lo que compraron antes de irse, esos datos ya no existen.
  3. **Riesgo legal**: en Chile, la Ley 20.169 (competencia desleal) y la normativa tributaria exigen conservar registros de transacciones por períodos determinados.
- **Alternativa mejor — baja lógica (soft delete)**: agregar un campo `activo BOOLEAN DEFAULT TRUE` en CLIENTES. "Dar de baja" a un cliente significa `UPDATE clientes SET activo = FALSE WHERE cliente_id = X`. El cliente ya no aparece en las operaciones del día a día (filtrando por `activo = TRUE`), pero sus ventas históricas siguen intactas y son consultables. La FK de VENTA → CLIENTE usa `ON DELETE RESTRICT`, que impide accidentalmente borrar un cliente con ventas.
- **Punto de cierre pedagógico**: este escenario demuestra que `ON DELETE CASCADE` no es intrínsecamente malo; es la política correcta en algunas relaciones (VENTA → DETALLE_VENTA: si se cancela una venta, sus líneas de detalle deben desaparecer también) e incorrecta en otras (CLIENTE → VENTA: las ventas tienen vida propia más allá del cliente). La regla es: cascade es apropiado cuando la entidad hija no tiene sentido de existencia sin la entidad padre, y restrictivo cuando la entidad hija tiene valor histórico o contable independiente.

---

**Pregunta 4 — FK auto-referencial y jerarquías** *(después del Desafío Rápido 2)*
> "El departamento de RRHH de TechStyle quiere registrar el organigrama de la empresa: cada empleado tiene un jefe directo, que a su vez tiene un jefe, y así hasta el CEO. ¿Cómo modelarías esto en una sola tabla EMPLEADO? ¿Qué pasa si el CEO (que no tiene jefe) intenta cumplir con un campo `jefe_id NOT NULL`? ¿Cómo escribirías una consulta SQL que traiga a todos los reportes directos del empleado con `id = 15`?"

Refuerza el patrón de FK auto-referencial en un contexto distinto al de CATEGORIA, y plantea el caso borde de la raíz de la jerarquía.

**Respuesta de referencia:**
- **Modelo**: `EMPLEADO(empleado_id PK, nombre, cargo, jefe_id FK → EMPLEADO)`. El campo `jefe_id` debe ser `INT NULL` (no `NOT NULL`), porque el CEO no tiene jefe.
- **El CEO y el NULL**: `jefe_id = NULL` es la forma correcta de representar "este nodo no tiene padre". Es el único caso en que NULL tiene semántica de negocio clara: "no aplica", no "desconocido". Declarar `jefe_id NOT NULL` impediría insertar al CEO — o obligaría a hacer que el CEO sea "su propio jefe" (`jefe_id = empleado_id`), lo que genera una FK circular que puede causar problemas en algunas operaciones.
- **Consulta SQL para reportes directos**:
  ```sql
  SELECT nombre, cargo
  FROM empleado
  WHERE jefe_id = 15;
  ```
  Esta consulta trae solo el nivel inmediato. Para toda la jerarquía descendente (todos los reportes, los reportes de los reportes, etc.) se necesita una consulta recursiva con `WITH RECURSIVE` — que está fuera del alcance de W05 pero es útil mencionarlo para que los estudiantes sepan que el modelo lo permite.
- **Punto de diseño**: la FK auto-referencial es el patrón que hace que MySQL pueda validar integridad referencial en la jerarquía: si se intenta insertar un empleado con `jefe_id = 9999` y no existe el empleado 9999, MySQL rechaza la inserción. Esto impide organigramas con referencias a jefes inexistentes.

---

**Pregunta 5 — Índices y decisiones estratégicas de consulta** *(al cierre)*
> "Roberto quiere que el CMI de TechStyle muestre, en tiempo real, el monto total de ventas del día actual filtrado por región, segmento de cliente y categoría de producto. Sin índices adicionales más allá de las PKs y FKs, ¿cuántas tablas debe recorrer MySQL para responder esta consulta? ¿Qué índices específicos agregarías para optimizarla y por qué?"

Conecta el concepto abstracto de índice con el KPI concreto que Roberto necesita, cerrando el argumento del curso.

**Respuesta de referencia:**
- **Tablas involucradas**: para calcular "ventas del día por región, segmento y categoría" se necesita un JOIN entre VENTAS (filtrar `fecha = hoy`), DETALLE_VENTA (para los montos), CLIENTES (para `region` y `segmento`), PRODUCTOS (para `categoria_id`) y CATEGORIA (para el nombre de la categoría). Son 5 tablas.
- **Sin índices adicionales**: MySQL usa los índices de PK para los JOINs (`cliente_id`, `producto_id`, `venta_id` como PKs). Pero para filtrar `ventas.fecha = hoy` sin índice, MySQL escanea todas las filas de VENTAS — que con 340.000 pedidos diarios pueden ser millones de registros acumulados. Similarmente, filtrar `clientes.region = 'Metropolitana'` sin índice escanea toda la tabla CLIENTES.
- **Índices recomendados**:
  ```sql
  CREATE INDEX idx_ventas_fecha ON ventas(fecha);
  -- Para el filtro de fecha en el WHERE principal

  CREATE INDEX idx_clientes_region ON clientes(region);
  CREATE INDEX idx_clientes_segmento ON clientes(segmento);
  -- Para los filtros del segmentador del CMI

  CREATE INDEX idx_productos_categoria ON productos(categoria_id);
  -- Para el JOIN con CATEGORIA
  ```
- **Índice compuesto opcional**: si los filtros de región y segmento siempre se aplican juntos, un índice compuesto `CREATE INDEX idx_clientes_region_segmento ON clientes(region, segmento)` es más eficiente que dos índices separados para ese caso específico.
- **Punto estratégico**: los índices tienen un costo de mantenimiento — MySQL los actualiza cada vez que se inserta, actualiza o elimina una fila. En una tabla con inserciones masivas (DETALLE_VENTA en Black Friday), demasiados índices ralentizan las escrituras. La regla práctica es indexar las columnas que aparecen en `WHERE`, `JOIN ON` y `ORDER BY` de las consultas más frecuentes y críticas, no todas las columnas posibles.

---

## 5. Essential Vocabulary

| Término | Definición operacional en el contexto del curso |
|---|---|
| **Actor (UML)** | Persona o sistema externo que interactúa con el sistema de información. Está fuera del límite del sistema. Genera casos de uso pero no necesariamente una entidad de la base de datos. En TechStyle: Cliente Web, Gerente de Ventas, Sistema de Pago Externo. |
| **Caso de Uso (UML)** | Acción que el sistema realiza para un actor. Se representa como una elipse con texto en infinitivo. Todo caso de uso que guarda o consulta información persistente genera al menos una entidad en el modelo de datos. |
| **Modelo Relacional** | Representación formal de las tablas de una base de datos en notación textual: `TABLA(`<u>`pk`</u>`, atributo, *fk*)`. Es la traducción del MER (visual) a una especificación implementable directamente en SQL. |
| **FK auto-referencial** | Clave foránea que referencia la clave primaria de la misma tabla. Implementa jerarquías de profundidad arbitraria (categorías, organigramas, árboles de cuentas) sin duplicar la estructura. El campo debe ser nullable para representar el nodo raíz (el que no tiene padre). |
| **MySQL Workbench** | Herramienta oficial de Oracle para diseño visual de bases de datos MySQL. Su EER Diagram (Enhanced Entity-Relationship) permite crear tablas, definir columnas y conectar entidades; el Forward Engineering genera el script DDL automáticamente. |
| **EER Diagram** | Enhanced Entity-Relationship Diagram. La vista de diseño visual de MySQL Workbench donde se crean entidades, se definen sus atributos y se conectan con herramientas de relación (1:N, N:M). Equivale al draw.io del lab W04 pero con generación automática de SQL. |
| **Forward Engineering** | Función de MySQL Workbench que genera el script SQL `CREATE TABLE` a partir del EER Diagram. Traduce el modelo visual a DDL ejecutable, incluyendo tipos de dato, PKs, FKs, índices y restricciones. |
| **AUTO_INCREMENT** | Propiedad de una columna INT en MySQL que genera automáticamente el siguiente valor entero disponible al insertar una nueva fila. Garantiza unicidad de IDs en sistemas multiusuario sin requerir que la aplicación calcule el siguiente valor. |
| **ON DELETE** | Política de integridad referencial que define qué ocurre con las filas hijas cuando se elimina la fila padre referenciada. Opciones: `RESTRICT` (bloquea la eliminación), `CASCADE` (elimina las hijas), `SET NULL` (pone NULL en la FK hija), `NO ACTION` (similar a RESTRICT, evaluado al final de la transacción). |
| **ON UPDATE** | Política de integridad referencial que define qué ocurre con las FKs hijas cuando se modifica la PK padre referenciada. `CASCADE` propaga el cambio automáticamente. En la práctica, si se usa `AUTO_INCREMENT`, las PKs rara vez cambian y esta política tiene menor relevancia operacional. |
| **Índice (Index)** | Estructura auxiliar que MySQL mantiene en paralelo a la tabla para permitir búsquedas rápidas sobre una columna sin escanear todas las filas. Las PKs siempre tienen índice; las FKs lo tienen en Workbench; columnas en `WHERE`, `JOIN ON` y `ORDER BY` frecuentes pueden necesitar índices adicionales. |
| **Soft Delete (baja lógica)** | Patrón de diseño que evita eliminar registros de la base de datos marcándolos como inactivos con un campo booleano (`activo = FALSE`). Preserva el historial de datos y la integridad referencial; el registro "eliminado" simplemente se filtra en las consultas operativas. |
| **DDL (Data Definition Language)** | Subconjunto de SQL que define la estructura de la base de datos: `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`. Es el lenguaje que genera Workbench con Forward Engineering y que los estudiantes ejecutarán en W06. |

---

## Notas de Coordinación Docente

- **Conexión con W04**: W05 resuelve la pregunta implícita que W04 dejó abierta: "¿cómo sé qué tablas necesita el sistema?" El MER de W04 modeló correctamente las entidades de datos centrales de TechStyle (CLIENTE, VENTA, PRODUCTO, DETALLE_VENTA), pero no las entidades de proceso (DESPACHO, DEVOLUCION) ni las entidades de soporte (PROVEEDOR, CATEGORIA). El UML explicita que esas entidades faltantes emergen de casos de uso que el analista debe identificar antes de diseñar. Si la Solemne 1 evidenció dificultad para distinguir cuándo crear una tabla nueva versus agregar una columna, este es el momento de reforzar: si el nuevo concepto tiene su propio ciclo de vida, atributos propios y relaciones con otras entidades, es una tabla nueva. Si es solo una propiedad adicional de una entidad existente, es una columna.

- **Conexión con W06–W07**: el script DDL que Workbench genera en el Lab W05 es el insumo exacto que los estudiantes ejecutarán en MySQL en W06. La coherencia entre el EER Diagram de W05 y la base de datos de W06 es crítica: si los nombres de las tablas o columnas difieren, los estudiantes no podrán reutilizar sus propios scripts. Conviene comunicar explícitamente en clase que el Lab W05 produce el "plano de arquitectura" que las próximas dos semanas construirán. El Forward Engineering de Workbench es su puente.

- **Conexión con W08–W09**: el modelo completo de TechStyle con 9 tablas (CLIENTE, VENTA, DETALLE_VENTA, PRODUCTO, CATEGORIA, PROVEEDOR, PROVEEDOR_PRODUCTO, DESPACHO, DEVOLUCION) es el sistema sobre el que se escribirán las consultas SQL de W08–W09. Los estudiantes que diseñen bien en W05 tendrán menos fricción en esas semanas. Los que tengan errores en el modelo (nombres incorrectos, FKs mal definidas, tablas intermedias mal estructuradas) encontrarán que sus consultas producen resultados incorrectos de formas que son difíciles de diagnosticar sin entender el modelo.

- **Gestión del tiempo en el Desafío Rápido 2 (FK auto-referencial)**: este desafío suele generar discusión extensa porque la jerarquía padre-hijo es un concepto nuevo. Si el tiempo es ajustado, priorizar la pregunta 3 (¿necesitas una nueva tabla CATEGORIA?) y la pregunta 3 (¿cómo representas la jerarquía?) sobre la pregunta 1 (modificación de PRODUCTO). La FK auto-referencial es el concepto más nuevo; lo demás es aplicación de lo visto en W04.

- **Demo de MySQL Workbench — requisitos técnicos**: la demo requiere MySQL Workbench instalado en el computador de clase. Verificar previamente que Workbench abre y que el Forward Engineering funciona sin conexión a un servidor MySQL (genera el SQL sin necesidad de ejecutarlo). Si hay problemas técnicos, las slides con el SQL generado son suficientes para la clase — la demo es ilustrativa, no el mecanismo de evaluación.

- **Perfil de estudiante y activación de conocimiento previo**: los estudiantes han usado Power BI con modelos estrella y copo de nieve. El modelo de 9 tablas de TechStyle es un copo de nieve pequeño (PRODUCTO → CATEGORIA con FK auto-referencial es el "copo"). Reconocer explícitamente esta conexión en clase: "el modelo que están diseñando hoy es el modelo que alimentaría el DW que conectarían a Power BI en un contexto profesional". Esto reduce la abstracción del diseño relacional y lo conecta con herramientas que ya dominan.

- **Errores frecuentes en el Lab W05**: (1) crear la tabla PROVEEDOR_PRODUCTO con solo dos columnas (las FKs) y olvidar los atributos propios de la relación como `precio_compra` y `proveedor_principal`; (2) modelar DESPACHO con FK a DETALLE_VENTA en vez de a VENTA — el despacho es de la venta completa, no de líneas individuales; (3) omitir el campo `categoria_padre_id` en CATEGORIA o declararlo NOT NULL, impidiendo la inserción de categorías raíz; (4) confundir Forward Engineering (modelo → SQL) con Reverse Engineering (base de datos existente → modelo) al usar Workbench por primera vez.

---

## 6. Online Reference Materials

### 6.1 UML y Diagramas de Casos de Uso

**Object Management Group (OMG) — "UML Specification"**
- URL: https://www.omg.org/spec/UML/
- Relevancia: la especificación oficial de UML del organismo que lo estandariza. No es necesario leerla completa; la sección sobre Use Case Diagrams (Capítulo 18 en UML 2.5.1) define los cuatro elementos usados en W05 con su semántica exacta. Útil para el profesor para verificar definiciones precisas y para contextualizar que UML es un estándar internacional de más de 25 años.

**Lucidchart — "UML Use Case Diagram Tutorial"**
- URL: https://www.lucidchart.com/pages/uml-use-case-diagram
- Relevancia: tutorial visual y accesible con ejemplos interactivos de diagramas de casos de uso. Cubre actores, casos de uso, relaciones `<<include>>` y `<<extend>>` (que no se enseñan en W05 pero pueden surgir como preguntas). Recomendable como referencia para estudiantes que quieran profundizar.

**Video — "Use Case Diagram — Step by Step Tutorial" (Lucidchart)**
- Buscar en YouTube: `"Use Case Diagram Tutorial Lucidchart"`.
- Duración: ~8 minutos. Muestra la construcción de un diagrama de casos de uso desde cero con un ejemplo de sistema de biblioteca. El nivel es apropiado y la metodología (identificar actores → identificar acciones → conectar) es la misma del curso.

---

### 6.2 MySQL Workbench y EER Diagrams

**MySQL — "MySQL Workbench Manual: EER Diagrams"**
- URL: https://dev.mysql.com/doc/workbench/en/wb-designing-tables.html
- Relevancia: la documentación oficial de MySQL Workbench para crear y gestionar EER Diagrams. Cubre la interfaz, la creación de tablas, la definición de relaciones y el Forward Engineering. Es la referencia directa para el Lab W05.

**MySQL — "MySQL Workbench Manual: Forward Engineering"**
- URL: https://dev.mysql.com/doc/workbench/en/wb-forward-engineering-sql-scripts.html
- Relevancia: describe paso a paso el proceso de Forward Engineering (exportar el modelo visual a SQL). Los estudiantes necesitarán seguir exactamente este proceso en el Lab W05. Recomendable como guía de referencia durante el laboratorio.

**Video — "MySQL Workbench Tutorial: Database Design & Modeling" (Traversy Media)**
- Buscar en YouTube: `"MySQL Workbench Tutorial Database Design Traversy Media"`.
- Duración: ~30 minutos. Cubre creación de EER Diagram, Forward Engineering y la interfaz de Workbench de forma práctica. El nivel y el ritmo son apropiados para los estudiantes del curso como preparación previa al Lab W05.

---

### 6.3 AUTO_INCREMENT e Integridad Referencial

**MySQL Reference Manual — "AUTO_INCREMENT Handling in InnoDB"**
- URL: https://dev.mysql.com/doc/refman/8.0/en/innodb-auto-increment-handling.html
- Relevancia: explica el comportamiento exacto de `AUTO_INCREMENT` en el motor InnoDB de MySQL, incluyendo qué ocurre con los valores cuando se eliminan filas (no se reutilizan por defecto). Este comportamiento es importante para entender por qué `cliente_id = 1, 2, 3, 7, 9` (con huecos) es normal y no indica corrupción de datos.

**MySQL Reference Manual — "Using FOREIGN KEY Constraints"**
- URL: https://dev.mysql.com/doc/refman/8.0/en/create-table-foreign-keys.html
- Relevancia: la referencia canónica para las opciones `ON DELETE` y `ON UPDATE`. Incluye ejemplos de cada comportamiento y las restricciones de uso (por ejemplo, `SET NULL` no puede usarse si la columna FK es `NOT NULL`). Los estudiantes la necesitarán en W06 cuando implementen las FK manualmente.

---

### 6.4 Índices en MySQL

**MySQL Reference Manual — "How MySQL Uses Indexes"**
- URL: https://dev.mysql.com/doc/refman/8.0/en/mysql-indexes.html
- Relevancia: explica los tipos de índices disponibles en MySQL, cuándo MySQL los utiliza automáticamente y cuándo es necesario crearlos manualmente. La sección "Column Indexes" es la más relevante para el nivel de W05.

**Percona — "MySQL Indexing Best Practices" (blog técnico)**
- URL: https://www.percona.com/blog/mysql-indexing-best-practices/
- Relevancia: artículo técnico de un referente en bases de datos MySQL que sintetiza las mejores prácticas de indexación con ejemplos de consultas. El nivel es levemente más avanzado que el de W05, pero la primera mitad del artículo (sobre cuándo crear índices y en qué columnas) es directamente aplicable y está escrita de forma accesible.
