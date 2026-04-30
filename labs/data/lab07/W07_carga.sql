-- ============================================================
-- W07_carga.sql  —  Carga de las 4 tablas faltantes
-- TechStyle · Laboratorio W07
-- ============================================================
-- INSTRUCCIÓN: reemplaza /ruta/a/ por la ruta real de tus archivos.
--   Windows : 'C:/Users/tu_usuario/Downloads/lab07/proveedores.csv'
--   Mac     : '/Users/tu_usuario/Downloads/lab07/proveedores.csv'
--   Linux   : '/home/tu_usuario/Downloads/lab07/proveedores.csv'
-- ============================================================

USE techstyle;

-- ── Paso 1: Habilitar LOAD DATA LOCAL INFILE (como root) ─────
-- Ejecuta esto una sola vez antes de continuar.
SET GLOBAL local_infile = 1;

-- Verifica que quedó activado (Value debe decir ON):
SHOW GLOBAL VARIABLES LIKE 'local_infile';

-- ── Paso 2: Cargar proveedores ────────────────────────────────
-- Columnas: proveedor_id, nombre_proveedor, rut, contacto, email, telefono
LOAD DATA LOCAL INFILE '/ruta/a/proveedores.csv'
    INTO TABLE proveedores
    CHARACTER SET utf8mb4
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS
    (proveedor_id, nombre_proveedor, rut, contacto, email, telefono);

SELECT COUNT(*) AS filas_cargadas FROM proveedores;
-- Resultado esperado: 4

-- ── Paso 3: Cargar proveedor_producto ─────────────────────────
-- Columnas: proveedor_id, producto_id, precio_compra, plazo_entrega_dias, proveedor_principal
LOAD DATA LOCAL INFILE '/ruta/a/proveedor_producto.csv'
    INTO TABLE proveedor_producto
    CHARACTER SET utf8mb4
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS
    (proveedor_id, producto_id, precio_compra, plazo_entrega_dias, proveedor_principal);

SELECT COUNT(*) AS filas_cargadas FROM proveedor_producto;
-- Resultado esperado: 10

-- ── Paso 4: Cargar despachos (con fechas NULL) ────────────────
-- Los despachos en estado Pendiente tienen fecha_despacho, fecha_entrega_estimada
-- y fecha_entrega_real vacíos en el CSV → se convierten a NULL con NULLIF.
LOAD DATA LOCAL INFILE '/ruta/a/despachos.csv'
    INTO TABLE despachos
    CHARACTER SET utf8mb4
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS
    (venta_id, direccion_entrega, @fecha_despacho, @fecha_entrega_estimada, @fecha_entrega_real, estado)
SET
    fecha_despacho          = NULLIF(@fecha_despacho, ''),
    fecha_entrega_estimada  = NULLIF(@fecha_entrega_estimada, ''),
    fecha_entrega_real      = NULLIF(@fecha_entrega_real, '');

SELECT * FROM despachos;
-- Resultado esperado: 3 filas
-- La fila con venta_id = 3 debe mostrar NULL en fecha_despacho,
-- fecha_entrega_estimada y fecha_entrega_real.

-- ── Paso 5: Cargar devoluciones ───────────────────────────────
-- monto_reembolsado está vacío (devolución aún Pendiente) → NULL con NULLIF.
LOAD DATA LOCAL INFILE '/ruta/a/devoluciones.csv'
    INTO TABLE devoluciones
    CHARACTER SET utf8mb4
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS
    (venta_id, producto_id, fecha_devolucion, cantidad_devuelta, motivo, estado, @monto_reembolsado)
SET
    monto_reembolsado = NULLIF(@monto_reembolsado, '');

SELECT COUNT(*) AS filas_cargadas FROM devoluciones;
-- Resultado esperado: 1

-- ── Paso 6: Verificación completa de la base de datos ────────
SELECT 'categorias'        AS tabla, COUNT(*) AS filas FROM categorias        UNION ALL
SELECT 'clientes',                   COUNT(*)           FROM clientes          UNION ALL
SELECT 'proveedores',                COUNT(*)           FROM proveedores       UNION ALL
SELECT 'productos',                  COUNT(*)           FROM productos         UNION ALL
SELECT 'ventas',                     COUNT(*)           FROM ventas            UNION ALL
SELECT 'detalle_ventas',             COUNT(*)           FROM detalle_ventas    UNION ALL
SELECT 'proveedor_producto',         COUNT(*)           FROM proveedor_producto UNION ALL
SELECT 'despachos',                  COUNT(*)           FROM despachos         UNION ALL
SELECT 'devoluciones',               COUNT(*)           FROM devoluciones;

-- Resultado esperado:
-- categorias         → 10
-- clientes           →  6
-- proveedores        →  4
-- productos          → 10
-- ventas             →  3
-- detalle_ventas     →  5
-- proveedor_producto → 10
-- despachos          →  3
-- devoluciones       →  1
