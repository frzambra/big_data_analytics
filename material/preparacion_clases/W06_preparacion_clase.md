# Professor's Class Brief — W06
## De los Planos a la Realidad: Implementación en MySQL, DDL, DML y Transacciones
**Curso**: Big Data y Analytics · ICOM E015 · Universidad San Sebastián
**Unidad**: 2 — Modelamiento y Gestión de Bases de Datos Relacionales
**Duración**: 1 hora 20 minutos (clase magistral)

---

## 1. Core Thesis

Esta sesión cierra el ciclo de diseño de TechStyle que abrió en W04 y lo convierte en infraestructura real. La tesis central es que **una base de datos correctamente implementada no es solo estructuralmente correcta — es operacionalmente confiable**, y esa confiabilidad no depende de la buena voluntad de los usuarios sino de los mecanismos que el motor de base de datos hace cumplir automáticamente: restricciones de tipo, restricciones de integridad referencial, y transacciones.

El primer movimiento argumental establece la diferencia entre el modelo en papel (el EER Diagram de W05) y el sistema real (la base de datos en MySQL Server). El modelo describe lo que debería ser; la implementación es lo que es. La ejecución del script DDL no es una operación técnica trivial: es el momento en que el diseño se vuelve ejecutable, los tipos de dato se vuelven verificables y las FK se convierten en reglas de negocio que MySQL hace cumplir en cada INSERT, UPDATE y DELETE. Un modelo que vive solo en Workbench no protege ningún dato; una base de datos en el servidor protege todos.

El segundo movimiento introduce el DML — `INSERT INTO` como la operación de carga inicial de datos — y establece un principio que los estudiantes deben internalizar: **el orden de inserción sigue la jerarquía del modelo**. No se pueden insertar ventas antes de insertar los clientes que las realizaron; no se pueden insertar productos sin las categorías a las que pertenecen. Este principio no es una regla arbitraria: es la consecuencia directa de que las FK están activas y MySQL verifica la existencia del registro padre antes de aceptar el registro hijo. Es también la primera vez en el curso en que los estudiantes experimentan la integridad referencial como un mecanismo activo, no como una propiedad del diagrama.

El tercer movimiento — el más denso conceptualmente — introduce las transacciones. El argumento de apertura es el escenario de Carlos: ¿qué pasa si al registrar una venta, el sistema falla después de crear la cabecera en VENTAS pero antes de crear las líneas en DETALLE_VENTA? Sin transacciones, queda una venta sin productos. Con transacciones, la pregunta tiene una respuesta binaria y confiable: o la venta completa existe, o no existe nada. Esta no es una garantía técnica abstracta: es la diferencia entre un sistema de información en el que Roberto puede confiar y uno que requiere auditorías manuales para detectar inconsistencias. Las propiedades ACID son el nombre formal de esa confianza.

El argumento de cierre regresa al punto de partida del curso: una base de datos es una representación estructurada de la realidad del negocio. Una base de datos con transacciones es una representación que también garantiza que esa realidad no puede quedar en un estado a medias. Los datos del CMI de Roberto son confiables no porque los analistas sean cuidadosos, sino porque el sistema los hace confiables por diseño.

---

## 2. Narrative Roadmap

La sesión tiene cuatro fases. Las dos primeras son procedimentales (DDL e INSERT) con énfasis en los principios que subyacen a los comandos; las dos últimas son conceptuales (transacciones y verificación). El hilo conductor es siempre la misma pregunta: ¿qué garantiza la confiabilidad de los datos que alimentan las decisiones de TechStyle?

### Fase 1 — Del Modelo al Sistema Real: Ejecutar el DDL (≈ 20 min)

La clase abre con el escenario de Roberto: el modelo está aprobado, el directorio quiere la base de datos funcionando el lunes. Juan tiene el script DDL generado en W05 y un servidor MySQL Server instalado. La pregunta no es técnica sino conceptual: ¿qué ocurre exactamente cuando ese script se ejecuta? ¿Qué pasa a existir que no existía antes?

La analogía de la arquitectura debe establecerse desde el inicio: el EER Diagram de Workbench es el plano; el script DDL es el plano de construcción; la base de datos en el servidor es el edificio. Los tres artefactos son distintos. Un plano no soporta cargas; el edificio sí. Un EER Diagram no valida integridad referencial; la base de datos sí.

**`CREATE DATABASE`** debe presentarse con énfasis en dos parámetros que los estudiantes tenderán a ignorar: `CHARACTER SET utf8mb4` y `COLLATE utf8mb4_spanish_ci`. Sin `utf8mb4`, la base de datos no puede almacenar caracteres especiales del español (ñ, tildes). Sin la collation correcta, comparaciones de texto como `WHERE region = 'Metropolitana'` pueden no funcionar como se espera. Estos no son detalles estéticos: en un sistema de producción en Chile, una base de datos con `latin1` generará errores de codificación en el 30% de los nombres de clientes.

El **Diccionario de Datos** debe introducirse como el contrato entre el analista y el sistema, no como un documento burocrático. Cada fila del diccionario especifica exactamente lo que MySQL verificará en cada operación: el tipo garantiza que un precio no puede almacenarse como texto; `NOT NULL` garantiza que una fecha de registro no puede omitirse; `CHECK` garantiza que el segmento de un cliente solo puede ser los tres valores que el negocio reconoce. El diccionario convierte las reglas de negocio en restricciones técnicas.

El **orden de creación de tablas** es el punto más operacionalmente crítico de esta fase. El profesor debe establecerlo como regla de oro: primero las tablas sin FK (padres), luego las que las referencian (hijos). Si se intenta crear VENTAS antes de crear CLIENTES, MySQL lanza un error porque la FK de `cliente_id` referencia una tabla que no existe. El error no es un defecto de MySQL: es la verificación correcta de que el modelo de datos es consistente. Este punto conecta directamente con el Lab W06 y el orden que los estudiantes deberán respetar al ejecutar su script.

`ON DELETE CASCADE` en `detalle_ventas` es la única desviación del `RESTRICT` por defecto que requiere justificación explícita en esta fase. El argumento: las líneas de detalle de una venta no tienen existencia independiente de su venta cabecera. Si se elimina una venta (por ejemplo, una cancelación completa), sus líneas de detalle no tienen sentido sin ella — y dejarlas en la base de datos crearía registros huérfanos. `CASCADE` implementa este invariante de negocio automáticamente. La regla general: `CASCADE` es correcto cuando la entidad hija no tiene valor histórico propio fuera del padre; `RESTRICT` cuando sí lo tiene.

### Fase 2 — Cargar Datos con INSERT INTO: el Orden es Inevitable (≈ 15 min)

Esta fase es más breve porque los conceptos son más concretos. El objetivo es establecer tres principios que los estudiantes usarán en el Lab W06.

**Principio 1 — La FK activa verifica en tiempo real**: el momento en que se ejecuta un INSERT en VENTAS con `cliente_id = 999`, MySQL verifica que el cliente 999 exista en CLIENTES. Si no existe, el INSERT falla con `ERROR 1452`. Esta no es una verificación diferida o eventual; ocurre en el mismo momento de la operación. Esto implica que cargar datos en una base de datos relacionales requiere respetar el orden del modelo, no solo el orden lógico de negocio.

**Principio 2 — `LAST_INSERT_ID()` en vez de números hardcodeados**: este es el punto más propenso a errores en la práctica de laboratorio. Si un estudiante inserta una venta con `INSERT INTO ventas...` y luego escribe `INSERT INTO detalle_ventas (venta_id, ...) VALUES (3, ...)`, el número 3 es correcto solo si esa venta es exactamente la tercera. En cualquier otro escenario — si ejecuta el script dos veces, si otro usuario ya insertó datos, si borró alguna venta — el número 3 puede ser incorrecto o referir a otra venta. `LAST_INSERT_ID()` captura el ID generado por el `AUTO_INCREMENT` de la sesión actual, sin depender de contar manualmente. El profesor debe demostrar ambas versiones y hacer explícito por qué la segunda es la única correcta en sistemas reales.

**Principio 3 — Verificación inmediata después de cada carga**: desarrollar el hábito de `SELECT COUNT(*) FROM nombre_tabla` después de cada INSERT masivo es una práctica de higiene de datos, no un extra optativo. En el Lab W06, los estudiantes que no verifican sus inserts descubrirán problemas en la Parte 5 (transacciones) cuando los datos no están donde esperaban. Esta es una oportunidad para conectar con el trabajo de datos profesional: el analista de datos no asume que la carga fue exitosa; lo verifica.

El **Desafío Rápido 2** sobre el INSERT de Nike Air Max debe provocar la distinción entre omitir una columna con DEFAULT y poner NULL explícitamente. Este punto parece menor pero reaparece constantemente en el trabajo práctico: si un estudiante omite `stock` en un INSERT de PRODUCTOS, obtiene `stock = 0` (porque el DEFAULT es 0), lo cual puede ser correcto o incorrecto dependiendo del contexto. Comprender la diferencia entre "el sistema decide" (omitir) y "yo decido" (poner NULL o un valor específico) es parte de la alfabetización SQL.

### Fase 3 — Transacciones: El Sistema Nervioso de la Confiabilidad (≈ 30 min)

Esta es la fase conceptualmente más importante de la sesión y debe recibir el tiempo que corresponde. Las transacciones son el mecanismo que separa una base de datos de una colección de archivos — y el concepto más cercano a los principios de ingeniería que los estudiantes de Ingeniería Comercial necesitan entender para tomar decisiones sobre sistemas de información.

**La apertura con el escenario de Carlos** es fundamental. El escenario de la venta que falla a mitad de camino no es hipotético: es el escenario de cualquier sistema que recibe tráfico concurrente y donde los procesos pueden interrumpirse por fallas de red, errores de validación o cortes de luz. El profesor debe hacer que los estudiantes sientan la gravedad del problema antes de introducir la solución. Si el sistema registra la venta pero no descuenta el stock, el CMI de Roberto muestra un stock incorrecto. Si descuenta el stock pero no registra la venta, los ingresos reportados son incorrectos. Ambos casos son errores de negocio con consecuencias reales: decisiones de reabastecimiento incorrectas, reportes financieros inconsistentes, auditorías fallidas.

**La definición de transacción** debe presentarse con énfasis en su propiedad más importante antes de las propiedades ACID: una transacción es una unidad indivisible de trabajo. La división entre "trabajo que ocurrió" y "trabajo que no ocurrió" es binaria. No existen estados intermedios persistentes visibles para el resto del sistema. Esto es lo que los estudiantes necesitan internalizar antes de memorizar ACID.

**El flujo `START TRANSACTION / COMMIT / ROLLBACK`** debe demostrarse paso a paso, con énfasis en qué ve cada actor durante la transacción:
- El usuario que ejecuta la transacción ve los cambios inmediatamente después de cada sentencia.
- Otros usuarios conectados simultáneamente **no ven los cambios** hasta el COMMIT.
- Si ocurre un error y se hace ROLLBACK, los cambios desaparecen como si nunca hubieran ocurrido — incluso para el usuario que los ejecutó.

Esta propiedad de aislamiento (la "I" de ACID) es lo que permite que TechStyle tenga múltiples vendedores operando simultáneamente sin que las ventas parciales de uno interfieran con los datos del otro.

**Las propiedades ACID** deben presentarse con ejemplos de TechStyle para cada propiedad, no como definiciones abstractas:
- **Atomicidad**: la venta de Juan (INSERT en VENTAS + INSERT en DETALLE_VENTA × 2 + UPDATE en PRODUCTOS × 2) ocurre completa o no ocurre. Nunca hay una venta con solo uno de los cinco cambios.
- **Consistencia**: al hacer COMMIT, MySQL verifica todas las FK, CHECK y NOT NULL. Si cualquiera falla, el COMMIT no ocurre. La base de datos pasa de un estado válido a otro estado válido — nunca a un estado inválido.
- **Aislamiento**: mientras Juan está en el medio de su venta, María no puede ver el estado parcial. Los datos que María lee son siempre el resultado de transacciones completamente confirmadas.
- **Durabilidad**: una vez que Juan recibe confirmación del COMMIT, los datos están en disco. Un corte de luz inmediatamente después del COMMIT no los pierde — MySQL escribe al log de transacciones antes de confirmar.

El punto pedagógico de cierre es explícito: las propiedades ACID son la razón por la que Roberto puede confiar en que el número que ve en el CMI es el número correcto, no el número que alguien olvidó confirmar, o el número de una transacción que falló a mitad de camino.

**El Desafío Rápido 3** sobre los tres escenarios de COMMIT/ROLLBACK debe manejarse con cuidado. El escenario más pedagógicamente rico es el segundo (500 productos, error en la fila 231): la respuesta correcta es ROLLBACK porque un catálogo parcial es peor que ningún catálogo — los reportes de María mostrarían datos incompletos de categorías. Este escenario conecta directamente con la práctica de ETL que los estudiantes encontrarán en la Unidad 3.

### Fase 4 — Verificación y Mantenimiento: Diagnóstico y ALTER TABLE (≈ 15 min)

Esta fase es más breve pero operacionalmente crítica. Los tres comandos de diagnóstico (`SHOW TABLES`, `DESCRIBE`, `SHOW CREATE TABLE`) son las herramientas que Juan usará inmediatamente después de ejecutar el script DDL para confirmar que la implementación es correcta. El profesor debe presentarlos como hábitos de trabajo, no como comandos de emergencia.

**`DESCRIBE tabla`** es el más importante. En 5 columnas muestra todo lo que el analista necesita saber para trabajar con una tabla: nombre de columna, tipo, si acepta NULL, si tiene índice y el valor por defecto. Memorizar este comando reduce a cero el tiempo que los estudiantes pasarán buscando "¿cuál era el tipo de dato de esta columna?" en sus scripts.

**`ALTER TABLE`** debe presentarse como la respuesta correcta a la pregunta implícita: "¿qué hago si necesito cambiar algo después de crear las tablas?". La respuesta incorrecta — que muchos estudiantes adoptarán si no se guía explícitamente — es eliminar la base de datos, corregir el script y recrear todo. `ALTER TABLE` permite agregar columnas, modificar tipos y agregar índices sin perder los datos existentes. En producción, este punto es crítico: una tabla con 8,5 millones de filas no se puede recrear sin un proceso de migración planificado. En el contexto del Lab W06, el mensaje es más simple: si se olvidaron de agregar un índice o una columna en el script DDL, `ALTER TABLE` lo agrega sin borrar nada.

---

## 3. Key Visual Evidence

| Visual | Recurso | Argumento que ilustra |
|---|---|---|
| **Diagrama de arquitectura MySQL** (grafo Mermaid con servidor → base de datos → tablas) | Slide con bloque `{mermaid}` — 3 niveles | Establece que un servidor MySQL contiene múltiples bases de datos, cada una con múltiples tablas. Sin este visual, los estudiantes confunden "la base de datos" (el servidor) con "una base de datos" (el esquema `techstyle`). La jerarquía es el fundamento conceptual del `CREATE DATABASE` y el `USE techstyle`. |
| **Tabla del Diccionario de Datos — CLIENTES** | Slide tabla (7 columnas: atributo, tipo, NOT NULL, restricción, descripción) | Demuestra que el diccionario no es documentación retrospectiva sino especificación prospectiva: cada fila define exactamente lo que MySQL verificará. Cuando el estudiante ve que `segmento` tiene `CHECK IN ('Premium', 'Estándar', 'Básico')`, entiende que intentar insertar `'premium'` (minúscula) fallará — no por descuido del programador sino por diseño del sistema. |
| **Slides de CREATE TABLE con comentarios** (tablas sin FK, tablas con FK, tabla con PK compuesta) | Tres slides consecutivos de código SQL | La progresión de tres slides muestra el mismo principio (cada entidad del MER se convierte en una tabla) aplicado a casos con complejidad creciente. El `ON DELETE CASCADE` en `detalle_ventas` debe tener comentario explícito: es el único CASCADE justificado y los estudiantes deben notar que el resto usa RESTRICT. |
| **Diagrama de flujo COMMIT/ROLLBACK** (Mermaid flowchart con nodos verde y rojo) | Slide con bloque `{mermaid}` — 6 nodos | Este es el visual más importante de la sesión de transacciones. El flujo `START TRANSACTION → INSERT → INSERT → UPDATE → UPDATE → ¿Todo OK? → COMMIT/ROLLBACK` hace tangible la atomicidad: todos los pasos deben completarse, o ninguno persiste. El color verde del COMMIT y rojo del ROLLBACK refuerzan la dualidad. |
| **Tabla de propiedades ACID** (4 filas: nombre, significado, en TechStyle) | Slide tabla (3 columnas) | ACID en abstracto es memorizable pero no comprensible. La columna "En TechStyle" convierte cada propiedad en una afirmación concreta sobre el sistema que los estudiantes están construyendo: "Atomicidad: la venta de Juan ocurre completa o no ocurre." Esto conecta la formalidad del concepto con su consecuencia práctica para Roberto. |
| **Código de transacción completa** (START TRANSACTION → 5 sentencias → COMMIT) | Slide con bloque de código SQL | Muestra el patrón completo que los estudiantes replicarán en el Lab W06. Debe incluir `SET @variable = LAST_INSERT_ID()` explícitamente: este es el primer uso de una variable de sesión en el curso y requiere atención. El comentario junto a `LAST_INSERT_ID()` debe explicar por qué no se usa el número directamente. |

**Nota para el profesor**: el slide del diccionario de datos de PRODUCTOS (`DECIMAL(10,2)` para precio) puede usarse para discutir por qué no se usa `FLOAT`. `FLOAT(10.99)` puede almacenarse internamente como `10.990000152587891` debido a la representación binaria de los flotantes. `DECIMAL(10,2)` almacena exactamente `10.99`. Para sistemas financieros, esta diferencia no es académica: un cálculo de impuesto que suma 50.000 transacciones con errores de flotante de 0,00001 puede acumular decenas de pesos de error en el total — lo que crea inconsistencias con el sistema contable.

---

## 4. Discussion Benchmarks

**Pregunta 1 — Diseño del script DDL y errores de orden** *(después de la explicación de CREATE TABLE)*
> "Juan ejecuta el siguiente script en orden: primero crea la tabla VENTAS, luego CLIENTES, luego DETALLE_VENTAS. MySQL lanza un error en la primera sentencia. ¿Por qué? ¿Cómo corriges el script? Ahora, Juan re-ejecuta el script corregido y MySQL lanza ERROR 1050: 'Table already exists'. ¿Por qué? ¿Cómo evitas este error sin eliminar la base de datos completa?"

Esta pregunta obliga a aplicar el principio del orden de creación y, además, introduce el problema práctico de la re-ejecución — que es el error más frecuente en el laboratorio.

**Respuesta de referencia:**
- **Error por orden incorrecto**: al intentar crear VENTAS antes de CLIENTES, la FK `ventas.cliente_id → clientes.cliente_id` referencia una tabla que no existe. MySQL no puede crear una FK hacia algo inexistente. Error: `ERROR 1215: Cannot add foreign key constraint`. Corrección: crear primero CLIENTES (y CATEGORIAS, PROVEEDORES), luego las tablas dependientes en orden de jerarquía.
- **ERROR 1050 en la segunda ejecución**: la tabla ya fue creada en la primera ejecución (aunque fallara parcialmente). Las tablas que se crearon antes del error aún existen. Solución 1: agregar `DROP TABLE IF EXISTS` antes de cada `CREATE TABLE` (lo que hace Workbench con la opción "Generate DROP Statements"). Solución 2: usar `CREATE TABLE IF NOT EXISTS`, que ignora el error si la tabla ya existe. Solución 3: `DROP DATABASE techstyle; CREATE DATABASE techstyle;` y re-ejecutar — apropiado solo en entorno de desarrollo, nunca en producción.
- **Punto pedagógico clave**: la diferencia entre `DROP TABLE IF EXISTS` antes del CREATE (borra y recrea) y `CREATE TABLE IF NOT EXISTS` (no hace nada si ya existe) tiene consecuencias distintas. El primero garantiza que la tabla refleja exactamente el script actual; el segundo puede dejar una tabla obsoleta si la definición cambió. En el Lab W06, los estudiantes usarán el script generado por Workbench con `DROP TABLE IF EXISTS` — que es el comportamiento correcto para un entorno de desarrollo donde se ejecuta el script varias veces.

---

**Pregunta 2 — El problema del precio histórico** *(después del segmento de INSERT INTO)*
> "Roberto le dice a Juan: 'El precio del Nike Air Max subió de $89.990 a $94.990 este mes. Actualiza `productos.precio_venta`. ¿Qué pasa con el informe de ventas del trimestre pasado? ¿Las ventas de enero ahora mostrarán el precio nuevo o el precio que el cliente pagó realmente?'"

Esta es una de las preguntas más reveladoras del curso porque conecta una decisión de diseño aparentemente menor (¿dónde almacenar el precio?) con la confiabilidad de los reportes históricos.

**Respuesta de referencia:**
- **El problema**: si el informe calcula el ingreso como `SUM(cantidad * productos.precio_venta)`, después de actualizar el precio a $94.990, todas las ventas históricas mostrarán el precio nuevo aunque el cliente pagó $89.990. El informe de ingresos del trimestre pasado aumenta artificialmente. Las ventas de enero "nunca ocurrieron" a $94.990; ese precio no existía entonces.
- **La solución que ya está implementada**: `detalle_ventas.precio_unitario` almacena el precio en el momento de la venta. El ingreso real se calcula como `SUM(cantidad * precio_unitario)` — usando el precio histórico, no el precio actual del catálogo. Actualizar `productos.precio_venta` no afecta ningún registro histórico de `detalle_ventas`.
- **El principio general**: en cualquier tabla que registre un evento (una venta, una transferencia, una nómina), los valores que entran en el cálculo del evento deben almacenarse en el momento en que ocurrió el evento. `precio_unitario` es el precio del producto en el momento de la venta. `sueldo_pagado` en una tabla de nóminas es el sueldo en el momento del pago. Calcular esos valores consultando las tablas maestras actuales produce reportes históricos incorrectos.
- **Extensión del principio**: este mismo argumento explica por qué `descuento_pct` está en `detalle_ventas`: los descuentos son condiciones de la transacción específica, no del producto. Una campaña de Black Friday con 30% puede terminar, pero las ventas realizadas durante esa campaña deben reflejar el 30% aplicado, no el 0% del catálogo normal.

---

**Pregunta 3 — Diseñar una transacción para un proceso de negocio real** *(después de la introducción a transacciones)*
> "TechStyle implementa un programa de puntos: por cada $1.000 en compras, el cliente acumula 10 puntos. Al registrar una venta, el sistema debe: (1) insertar la venta, (2) insertar el detalle, (3) descontar el stock, (4) calcular los puntos ganados y sumarlos al saldo del cliente en la tabla CLIENTES_PUNTOS. ¿Cómo diseñarías la transacción? ¿Qué pasa si el paso 4 falla porque la tabla CLIENTES_PUNTOS no existe todavía?"

Esta pregunta amplía el escenario de transacciones del curso y obliga a pensar en la atomicidad cuando hay un proceso de negocio compuesto por más pasos de los habituales.

**Respuesta de referencia:**
- **Diseño de la transacción**:
  ```sql
  START TRANSACTION;
  -- Paso 1: crear la venta
  INSERT INTO ventas (fecha, cliente_id) VALUES (CURDATE(), @cliente_id);
  SET @nueva_venta = LAST_INSERT_ID();
  -- Paso 2: insertar detalle
  INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario)
  VALUES (@nueva_venta, @producto_id, @cantidad, @precio);
  -- Paso 3: descontar stock
  UPDATE productos SET stock = stock - @cantidad WHERE producto_id = @producto_id;
  -- Paso 4: acumular puntos (monto / 1000 * 10)
  UPDATE clientes_puntos
  SET puntos_acumulados = puntos_acumulados + ((@cantidad * @precio) / 1000 * 10)
  WHERE cliente_id = @cliente_id;
  COMMIT;
  ```
- **Si el paso 4 falla porque la tabla no existe**: MySQL lanzará `ERROR 1146: Table 'techstyle.clientes_puntos' doesn't exist`. La sentencia falla pero la transacción sigue abierta. Los pasos 1, 2 y 3 ocurrieron dentro de la transacción pero no están confirmados. Si se ejecuta `ROLLBACK`, ninguno de los cuatro cambios persiste. Si el código de la aplicación no maneja el error y no ejecuta ROLLBACK, la transacción puede quedar abierta hasta que se cierra la sesión — dejando bloqueos activos sobre las tablas.
- **La decisión de diseño**: ¿debe la ausencia de la tabla CLIENTES_PUNTOS impedir registrar la venta? Depende de la política de negocio. Si los puntos son un beneficio opcional, tal vez la venta debe confirmarse aunque los puntos fallen (dos transacciones separadas: una para la venta y otra para los puntos). Si los puntos son un contrato con el cliente (como en un programa de lealtad regulado), la atomicidad debe incluir los puntos. Este es el tipo de decisión que el analista de datos debe escalar al área de negocio, no decidir técnicamente.
- **Punto pedagógico clave**: el diseño de una transacción no es solo técnico — refleja una decisión de negocio sobre qué operaciones deben ser atómicas. La pregunta "¿qué debe pasar si falla X?" es siempre una pregunta de negocio antes de ser una pregunta técnica.

---

**Pregunta 4 — ACID en un escenario de Black Friday** *(después de la tabla de propiedades ACID)*
> "TechStyle tiene Black Friday: 12.000 ventas en los primeros 15 minutos. Tres vendedores del call center están registrando ventas del mismo producto (Nike Air Max, stock inicial = 150 unidades) simultáneamente. Sin la propiedad de Aislamiento, ¿qué podría ocurrir? ¿Cómo previene MySQL este problema?"

Esta pregunta hace tangibles los problemas de concurrencia que ACID resuelve, en un contexto de negocio que los estudiantes pueden imaginar.

**Respuesta de referencia:**
- **Sin aislamiento — el problema de la lectura sucia**: el Vendedor A inicia una transacción, lee que hay 150 unidades de Nike Air Max y vende 10. En su transacción (no confirmada aún), el stock bajó a 140. El Vendedor B, simultáneamente, lee el stock de la tabla y ve 140 (la lectura sucia del cambio no confirmado de A). B vende 10 también y baja el stock a 130. Ambos hacen COMMIT. El stock final es 130, pero se vendieron 20 unidades cuando debería haber bajado a 130 (correcto) o a 120 (si A y B leyeron ambos el valor original de 150).
- **Problema más grave — la actualización perdida**: sin aislamiento, A y B pueden leer ambos el stock como 150, ejecutar simultáneamente `UPDATE productos SET stock = stock - 10`, y el resultado puede ser que solo uno de los dos cambios persista — el último en confirmar sobreescribe al primero. TechStyle vendería 20 unidades pero el stock solo bajaría en 10.
- **Cómo MySQL previene esto**: el motor InnoDB usa bloqueos a nivel de fila (row-level locking) para transacciones. Cuando A hace `UPDATE productos SET stock = stock - 10`, MySQL bloquea la fila del Nike Air Max hasta el COMMIT de A. B debe esperar hasta que A confirme o deshaga antes de poder actualizar la misma fila. El resultado es siempre correcto: si A vendió 10 y B vendió 10, el stock final es 130.
- **Punto de matiz para el docente**: el nivel de aislamiento por defecto de MySQL InnoDB es `REPEATABLE READ`, que previene lecturas sucias pero permite "phantom reads" en ciertos patrones de consulta. Para el nivel de W06, este nivel de detalle no es necesario — el punto pedagógico es que MySQL gestiona la concurrencia automáticamente y que las transacciones son el mecanismo que lo hace posible.

---

**Pregunta 5 — El verdadero costo de no usar transacciones** *(al cierre)*
> "Un desarrollador del equipo de TechStyle argumenta: 'Las transacciones ralentizan el sistema. Para Black Friday, cuando hay 12.000 ventas en 15 minutos, deberíamos deshabilitar las transacciones para mejorar el rendimiento. Podemos hacer la conciliación contable al final del día.' ¿Es correcta esta decisión? ¿Qué le responderías?"

Esta es la pregunta de cierre. Obliga a los estudiantes a argumentar a favor de las transacciones desde el punto de vista del negocio, no solo desde la perspectiva técnica.

**Respuesta de referencia:**
- **¿Ralentizan las transacciones el sistema?** Las transacciones tienen un overhead de escritura en el log de transacciones (WAL — Write-Ahead Log), que es real pero marginal en hardware moderno. El overhead de una transacción bien diseñada es de microsegundos, no de segundos. En cambio, el costo de reparar inconsistencias después del hecho — una "conciliación contable al final del día" con datos inconsistentes — puede ser de horas o días de trabajo humano.
- **¿Qué pasa con los 12.000 pedidos?** Sin transacciones, en 15 minutos de tráfico intenso con fallas de red, interrupciones de proceso o errores de validación, puede haber cientos de ventas parcialmente registradas: ventas sin detalle, stock descontado sin venta registrada, o ventas registradas sin descuento de stock. La "conciliación al final del día" requiere identificar cada uno de esos casos y corregirlos manualmente — asumiendo que es posible identificarlos, lo que no siempre es así.
- **El argumento financiero**: en una empresa que factura $500M anuales, un día de Black Friday puede representar $5M en ventas. Inconsistencias de datos en ese día — incluso del 1% de las transacciones — son $50.000 en datos incorrectos. El costo de la "optimización" que propone el desarrollador es órdenes de magnitud mayor que el overhead de las transacciones.
- **Punto pedagógico final**: las transacciones no son un lujo técnico para sistemas con poco tráfico. Son el fundamento de cualquier sistema de información en el que se toman decisiones basadas en datos. Roberto no puede confiar en el CMI del día siguiente si las ventas de Black Friday no tienen integridad transaccional.

---

## 5. Essential Vocabulary

| Término | Definición operacional en el contexto del curso |
|---|---|
| **DDL (Data Definition Language)** | Subconjunto de SQL que define y modifica la estructura de la base de datos: `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`. Es el lenguaje que convierte el MER en tablas reales en el servidor. Distinguir de DML (que manipula datos) y DQL (que los consulta). |
| **DML (Data Manipulation Language)** | Subconjunto de SQL que manipula los datos dentro de las tablas: `INSERT`, `UPDATE`, `DELETE`. Opera sobre la estructura creada por el DDL. Las transacciones controlan cuándo los cambios DML se vuelven permanentes. |
| **`CHARACTER SET utf8mb4`** | Codificación de caracteres que soporta todo el Unicode, incluyendo caracteres del español (ñ, tildes), árabe, chino y emojis. Es la opción correcta para cualquier base de datos en contextos latinoamericanos. `latin1` o `utf8` (la versión de 3 bytes de MySQL) son insuficientes para el español completo. |
| **`COLLATE utf8mb4_spanish_ci`** | Regla de comparación de texto que define el orden y la equivalencia de caracteres para el alfabeto español (`ci` = case-insensitive). Con la collation correcta, `ORDER BY apellido` respeta el orden del español; comparaciones como `WHERE nombre = 'María'` funcionan con o sin tilde según las reglas del idioma. |
| **`DECIMAL(p, s)`** | Tipo de dato numérico de precisión exacta: `p` dígitos totales, `s` dígitos decimales. Obligatorio para valores monetarios. `FLOAT` y `DOUBLE` son aproximaciones binarias que pueden acumular errores de redondeo en sumas de muchas filas — inaceptable para aplicaciones financieras. |
| **`AUTO_INCREMENT`** | Propiedad de columnas INT que genera automáticamente el siguiente valor disponible al insertar una fila. El motor InnoDB garantiza unicidad incluso con inserciones concurrentes mediante un bloqueo interno del contador. Los valores no se reutilizan si se eliminan filas (hay "huecos" en la secuencia). |
| **`LAST_INSERT_ID()`** | Función MySQL que devuelve el último valor generado por `AUTO_INCREMENT` en la sesión actual. Solo refleja los cambios de la sesión propia, no los de otras conexiones concurrentes. Es la forma correcta de referenciar el ID recién creado en sentencias DML subsiguientes de la misma sesión. |
| **Transacción** | Conjunto de operaciones DML que se ejecutan como una unidad atómica. Se inicia con `START TRANSACTION`, se confirma con `COMMIT` (los cambios son permanentes y visibles para otros) o se deshace con `ROLLBACK` (los cambios desaparecen como si no hubieran ocurrido). |
| **COMMIT** | Sentencia que confirma definitivamente todos los cambios de la transacción activa, los escribe en disco y los hace visibles para otras sesiones. Después de un COMMIT, los cambios sobreviven a un reinicio del servidor. |
| **ROLLBACK** | Sentencia que deshace todos los cambios de la transacción activa, devolviendo la base de datos exactamente al estado en que estaba antes del `START TRANSACTION`. Puede ocurrir por decisión explícita del usuario o automáticamente si MySQL detecta un error crítico. |
| **Propiedades ACID** | Las cuatro garantías de confiabilidad de una transacción: **A**tomicidad (todo o nada), **C**onsistencia (la BD pasa de un estado válido a otro), **I**solamiento (las transacciones no se interfieren entre sí), **D**urabilidad (un COMMIT sobrevive a fallas del sistema). Son el contrato de confiabilidad entre el motor de base de datos y la aplicación. |
| **`DESCRIBE tabla`** | Comando MySQL que muestra la estructura de una tabla: nombre de columna, tipo de dato, si acepta NULL, tipo de índice (PRI, UNI, MUL) y valor por defecto. Es el comando de diagnóstico más útil en el trabajo diario con MySQL. Equivale a "¿qué contiene esta tabla y qué restricciones tiene?" |
| **`ALTER TABLE`** | Sentencia DDL que modifica la estructura de una tabla existente sin necesidad de recrearla ni de perder los datos. Permite agregar/eliminar columnas (`ADD COLUMN`, `DROP COLUMN`), modificar tipos (`MODIFY COLUMN`), agregar índices (`ADD INDEX`) y modificar FK. En producción, es la única forma segura de evolucionar el esquema de una tabla con datos. |
| **Precio histórico** | El valor de un atributo en el momento en que ocurrió una transacción, en contraste con su valor actual en la tabla maestra. En `detalle_ventas`, `precio_unitario` es el precio histórico de la venta — distinto de `productos.precio_venta`, que es el precio actual del catálogo. Los reportes históricos siempre deben usar el precio histórico. |
| **Soft delete (baja lógica)** | Patrón de diseño que evita borrar registros con valor histórico, marcándolos como inactivos con un campo `activo BOOLEAN`. Los registros "eliminados" se excluyen de consultas operativas con `WHERE activo = TRUE` pero permanecen disponibles para auditoría e historial. Es la alternativa correcta a `DELETE` en tablas con FK `ON DELETE RESTRICT`. |

---

## Notas de Coordinación Docente

- **Conexión con W05**: W06 ejecuta exactamente el script DDL que los estudiantes generaron en el Lab W05 (o el script de solución, si el lab W05 tuvo problemas). Si los grupos tuvieron dificultades en W05 — especialmente con el orden de las tablas o con el `ON DELETE CASCADE` en `detalle_ventas` — es útil abrir W06 con una revisión rápida del script corregido antes de pasar a la ejecución. Un script con errores producirá errores de FK en el servidor que confundirán a los estudiantes si no entienden el origen.

- **Conexión con W07**: el Lab W06 termina con la base de datos poblada con datos de prueba. W07 introduce las consultas SELECT con filtros, JOINs y agregaciones sobre esa misma base de datos. El estado de los datos al final de W06 importa: los estudiantes que tienen datos inconsistentes o incompletos en W06 tendrán resultados incorrectos o confusos en las consultas de W07. Vale la pena dedicar los últimos 5 minutos del Lab W06 a que cada grupo ejecute las consultas de diagnóstico del Paso 16 y confirme que todas retornan 0 filas.

- **Gestión del tiempo en la fase de transacciones**: esta fase es la que tiene mayor riesgo de extenderse. El Desafío Rápido 3 puede provocar discusiones largas, especialmente el escenario de los 500 productos con error en la fila 231. El punto pedagógico esencial es que la transacción abarca toda la carga masiva o ninguna parte de ella — no es necesario resolver todos los matices de los escenarios en clase. Si el tiempo es ajustado, postergar la discusión del tercer escenario (devolución con stock) al Lab W06.

- **El contexto de `autocommit` en MySQL**: MySQL tiene `autocommit = 1` por defecto. Esto significa que cada sentencia DML ejecutada fuera de un `START TRANSACTION` explícito es confirmada automáticamente como una transacción de una sola sentencia. Los estudiantes que ejecutan INSERTs sin `START TRANSACTION` en el lab están haciendo commits implícitos. Este comportamiento no es incorrecto para inserciones simples, pero elimina la posibilidad de hacer ROLLBACK si algo sale mal. El profesor puede demostrarlo con `SELECT @@autocommit;` y `SET autocommit = 0;` si el tiempo lo permite — aunque para W06 no es obligatorio.

- **Errores frecuentes en el Lab W06**:
  1. Ejecutar solo la sentencia seleccionada (botón ⚡ en Workbench) en vez de ejecutar todo el script (botón ⚡⚡). Solo el fragmento seleccionado se ejecuta, y el estudiante no entiende por qué "solo se crearon 3 tablas".
  2. Olvidar `USE techstyle;` al ejecutar scripts de INSERT. Las sentencias se ejecutan sobre la base de datos activa — si es otra (ej. `sys` o `information_schema`), los INSERTs fallan con "table doesn't exist" de forma confusa.
  3. Usar `LAST_INSERT_ID()` después de un segundo INSERT: si el estudiante inserta dos ventas consecutivas y usa `LAST_INSERT_ID()` en el segundo bloque de detalles, ese valor ahora apunta al ID de la segunda venta, no de la primera. Enseñar el patrón `SET @var = LAST_INSERT_ID()` inmediatamente después de cada INSERT en VENTAS.
  4. No ejecutar `ROLLBACK` manualmente después de un error dentro de una transacción. La transacción queda abierta y bloquea recursos. Enseñar que `ROLLBACK` siempre debe ir en el manejador de errores, no solo como alternativa condicional.

- **Perfil de estudiante — conexión con conocimiento previo**: los estudiantes conocen Power BI y Power Query. La carga de datos con INSERT INTO es el equivalente SQL de cargar tablas en el modelo de datos de Power BI. El concepto de que las relaciones entre tablas requieren que los datos padre existan antes que los datos hijo es exactamente el mismo que en el modelo estrella de Power BI: primero se cargan las tablas de dimensión, luego la tabla de hechos. Hacer explícita esta conexión reduce la sensación de que SQL es completamente nuevo; es la misma lógica en un nivel más bajo.

---

## 6. Online Reference Materials

### 6.1 DDL: CREATE TABLE y Tipos de Dato

**MySQL Reference Manual — "CREATE TABLE Statement"**
- URL: https://dev.mysql.com/doc/refman/8.0/en/create-table.html
- Relevancia: la referencia canónica para la sintaxis completa de `CREATE TABLE`. Cubre todos los tipos de restricciones (PRIMARY KEY, FOREIGN KEY, CHECK, UNIQUE), opciones de motor (InnoDB vs. MyISAM) y la diferencia entre `IF NOT EXISTS` y el comportamiento por defecto. Es la referencia que los estudiantes consultarán cuando encuentren errores de sintaxis en sus scripts.

**MySQL Reference Manual — "Data Types"**
- URL: https://dev.mysql.com/doc/refman/8.0/en/data-types.html
- Relevancia: la referencia completa de todos los tipos de dato en MySQL. Los más relevantes para W06 son INTEGER, DECIMAL, VARCHAR, DATE y TINYINT(1) para booleanos. El capítulo sobre DECIMAL vs. FLOAT es especialmente útil para la discusión sobre precios y valores monetarios.

**MySQL Reference Manual — "Character Sets and Collations"**
- URL: https://dev.mysql.com/doc/refman/8.0/en/charset.html
- Relevancia: explica por qué `utf8mb4` es preferible a `utf8` en MySQL (el `utf8` de MySQL solo usa 3 bytes y no soporta todos los caracteres Unicode). Para un curso en contexto chileno con nombres en español, esto no es un detalle técnico — es una fuente potencial de bugs en producción que vale la pena mencionar.

---

### 6.2 DML: INSERT y Gestión de Datos

**MySQL Reference Manual — "INSERT Statement"**
- URL: https://dev.mysql.com/doc/refman/8.0/en/insert.html
- Relevancia: cubre la sintaxis completa de INSERT, incluyendo inserción de múltiples filas en una sola sentencia (`INSERT INTO ... VALUES (...), (...), (...)`), el comportamiento de `DEFAULT` cuando se omite una columna, y la relación con `LAST_INSERT_ID()`. La sección sobre INSERT con `ON DUPLICATE KEY UPDATE` es un anticipo de consultas avanzadas para estudiantes que quieran profundizar.

**MySQL Reference Manual — "Information Functions — LAST_INSERT_ID()"**
- URL: https://dev.mysql.com/doc/refman/8.0/en/information-functions.html#function_last-insert-id
- Relevancia: documentación oficial de `LAST_INSERT_ID()`, incluyendo la especificación de que devuelve el ID de la sesión actual (no de otras conexiones concurrentes) y el comportamiento cuando una sentencia inserta múltiples filas. Útil para el docente para responder preguntas avanzadas sobre concurrencia.

---

### 6.3 Transacciones y Propiedades ACID

**MySQL Reference Manual — "InnoDB and the ACID Model"**
- URL: https://dev.mysql.com/doc/refman/8.0/en/mysql-acid.html
- Relevancia: la documentación oficial de MySQL sobre las propiedades ACID y cómo InnoDB las implementa. Cubre atomicidad (redo log y undo log), consistencia (restricciones de integridad), aislamiento (niveles de aislamiento) y durabilidad (doublewrite buffer). Nivel técnico apropiado para el profesor; puede citarse selectivamente en clase.

**MySQL Reference Manual — "Transaction Isolation Levels"**
- URL: https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html
- Relevancia: describe los cuatro niveles de aislamiento de transacciones en InnoDB (READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE). El nivel por defecto en MySQL es REPEATABLE READ. No es contenido de W06, pero el docente lo necesita para responder preguntas avanzadas sobre por qué dos transacciones simultáneas no se interfieren.

**Artículo — "ACID Compliance: What It Means and Why You Should Care" (Cockroach Labs)**
- URL: https://www.cockroachlabs.com/blog/acid-rain/
- Relevancia: explicación accesible de las propiedades ACID con ejemplos de sistemas bancarios y de e-commerce. El nivel es apropiado para estudiantes de Ingeniería Comercial — técnico pero orientado a las consecuencias de negocio de cada propiedad. Recomendable como lectura complementaria para estudiantes que quieran profundizar.

**Video — "Database Transactions & ACID Properties Explained" (ByteByteGo)**
- Buscar en YouTube: `"Database Transactions ACID ByteByteGo"`.
- Duración: ~7 minutos. Animación clara que explica las cuatro propiedades ACID con ejemplos de transferencias bancarias. El nivel y el formato visual son apropiados como repaso para los estudiantes antes del Lab W06.

---

### 6.4 Mantenimiento: ALTER TABLE

**MySQL Reference Manual — "ALTER TABLE Statement"**
- URL: https://dev.mysql.com/doc/refman/8.0/en/alter-table.html
- Relevancia: la referencia completa de `ALTER TABLE`. Los casos más relevantes para W06 son `ADD COLUMN`, `MODIFY COLUMN`, `ADD INDEX` y `ADD CONSTRAINT`. También cubre las limitaciones de ALTER TABLE en tablas con datos existentes (por ejemplo, agregar una columna `NOT NULL` sin `DEFAULT` en una tabla con filas falla si no se especifica un valor para las filas existentes).
