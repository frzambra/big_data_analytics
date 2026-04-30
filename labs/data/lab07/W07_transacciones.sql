-- ============================================================
-- W07_transacciones.sql  —  Transacciones COMMIT y ROLLBACK
-- TechStyle · Laboratorio W07
-- ============================================================

USE techstyle;

-- ════════════════════════════════════════════════════════════
-- PASO 7: TRANSACCIÓN EXITOSA — Venta de Sofía Ramírez (COMMIT)
-- ════════════════════════════════════════════════════════════
-- Registra una venta completa: cabecera, detalles, descuento
-- de stock y despacho, todo dentro de una misma transacción.

START TRANSACTION;

-- a) Crear la venta
INSERT INTO ventas (fecha, cliente_id) VALUES (CURDATE(), 4);  -- Sofía Ramírez
SET @venta_sofia = LAST_INSERT_ID();

-- b) Agregar los productos
INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, descuento_pct)
VALUES
    (@venta_sofia, 2, 1, 119990.00, 5.00),  -- Adidas Ultraboost con 5%
    (@venta_sofia, 6, 1,  44990.00, 0.00);  -- Pantalón Under Armour sin descuento

-- c) Descontar el stock
UPDATE productos SET stock = stock - 1 WHERE producto_id = 2;
UPDATE productos SET stock = stock - 1 WHERE producto_id = 6;

-- d) Crear el despacho como pendiente (direccion_entrega es NOT NULL)
INSERT INTO despachos (venta_id, direccion_entrega, estado)
VALUES (@venta_sofia, 'Av. Marta Colvin 10120, Las Condes, Santiago', 'Pendiente');

-- Confirmar todos los cambios atómicamente
COMMIT;

-- ── Verificaciones post-COMMIT ────────────────────────────────

-- ¿El stock se descontó correctamente?
SELECT producto_id, nombre_producto, stock
FROM productos
WHERE producto_id IN (2, 6);
-- Esperado: Adidas Ultraboost → 89 (era 90), Pantalón Under Armour → 94 (era 95)

-- ¿La venta, el detalle y el despacho quedaron registrados?
SELECT v.venta_id, v.fecha,
       dv.producto_id, dv.cantidad,
       d.estado AS estado_despacho
FROM ventas v
JOIN detalle_ventas dv ON v.venta_id = dv.venta_id
JOIN despachos d       ON v.venta_id = d.venta_id
WHERE v.cliente_id = 4;
-- Esperado: 2 filas (productos 2 y 6) con estado_despacho = 'Pendiente'


-- ════════════════════════════════════════════════════════════
-- PASO 8: TRANSACCIÓN CON ERROR — Venta de Diego Torres (ROLLBACK)
-- ════════════════════════════════════════════════════════════
-- Simula una operación que falla por violación de FK.
-- Resultado esperado: ningún dato queda registrado.

START TRANSACTION;

-- a) Crear la venta
INSERT INTO ventas (fecha, cliente_id) VALUES (CURDATE(), 5);  -- Diego Torres
SET @venta_diego = LAST_INSERT_ID();

-- b) Agregar un producto válido
INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario)
VALUES (@venta_diego, 8, 1, 39990.00);  -- Mochila Puma 20L (existe)

-- c) Intentar agregar un producto inexistente → provoca error de FK
INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario)
VALUES (@venta_diego, 99, 2, 15000.00);  -- producto_id = 99 NO existe

-- El INSERT anterior fallará con:
-- ERROR 1452 (23000): Cannot add or update a child row:
--   a foreign key constraint fails
-- La transacción queda ABIERTA con error pendiente.

-- Deshacer toda la operación (ejecutar manualmente en Workbench)
ROLLBACK;

-- ── Verificaciones post-ROLLBACK ──────────────────────────────

-- Diego Torres NO debe tener ventas
SELECT * FROM ventas WHERE cliente_id = 5;
-- Esperado: 0 filas

-- No debe haber despachos para ventas de Diego
SELECT * FROM despachos
WHERE venta_id IN (
    SELECT venta_id FROM ventas WHERE cliente_id = 5
);
-- Esperado: 0 filas
