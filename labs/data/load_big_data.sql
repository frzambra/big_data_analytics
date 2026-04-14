-- ============================================================
-- load_big_data.sql
-- Carga los 9 archivos CSV del modelo TechStyle W05 en MySQL.
-- Ejecutar DESPUÉS de generate_big_data.py
--
-- Desde terminal:
--   mysql --local-infile=1 -u root -p < load_big_data.sql
--
-- Tiempo estimado de carga: 15–30 min en laptop.
-- ============================================================

SET GLOBAL local_infile = 1;
SET NAMES utf8mb4;

-- ============================================================
-- Base de datos
-- ============================================================
DROP DATABASE IF EXISTS techstyle_bigdata;
CREATE DATABASE techstyle_bigdata
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_spanish_ci;

USE techstyle_bigdata;

-- ============================================================
-- DDL — mismo orden que W05 (tablas padre antes que hijas)
-- ============================================================

-- 1. categorias (auto-referencial)
CREATE TABLE categorias (
    categoria_id      INT          NOT NULL AUTO_INCREMENT,
    nombre_categoria  VARCHAR(50)  NOT NULL,
    descripcion       VARCHAR(200) NULL,
    categoria_padre_id INT         NULL,
    CONSTRAINT pk_categorias PRIMARY KEY (categoria_id),
    CONSTRAINT fk_cat_padre  FOREIGN KEY (categoria_padre_id)
        REFERENCES categorias (categoria_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- 2. clientes
CREATE TABLE clientes (
    cliente_id      INT          NOT NULL AUTO_INCREMENT,
    nombre          VARCHAR(50)  NOT NULL,
    apellido        VARCHAR(50)  NOT NULL,
    email           VARCHAR(100) NOT NULL,
    region          VARCHAR(50)  NOT NULL,
    segmento        VARCHAR(20)  NULL,
    fecha_registro  DATE         NOT NULL,
    CONSTRAINT pk_clientes       PRIMARY KEY (cliente_id),
    CONSTRAINT uq_clientes_email UNIQUE (email),
    CONSTRAINT chk_segmento_valido
        CHECK (segmento IN ('Premium','Estándar','Básico'))
);

-- 3. proveedores
CREATE TABLE proveedores (
    proveedor_id      INT          NOT NULL AUTO_INCREMENT,
    nombre_proveedor  VARCHAR(100) NOT NULL,
    rut               VARCHAR(12)  NOT NULL,
    contacto          VARCHAR(100) NULL,
    email             VARCHAR(100) NULL,
    telefono          VARCHAR(20)  NULL,
    CONSTRAINT pk_proveedores  PRIMARY KEY (proveedor_id),
    CONSTRAINT uq_prov_rut     UNIQUE (rut)
);

-- 4. productos
CREATE TABLE productos (
    producto_id     INT            NOT NULL AUTO_INCREMENT,
    nombre_producto VARCHAR(100)   NOT NULL,
    categoria_id    INT            NOT NULL,
    precio_venta    DECIMAL(10,2)  NOT NULL,
    costo_unitario  DECIMAL(10,2)  NOT NULL,
    stock           INT            NOT NULL DEFAULT 0,
    activo          TINYINT(1)     NOT NULL DEFAULT 1,
    CONSTRAINT pk_productos         PRIMARY KEY (producto_id),
    CONSTRAINT fk_prod_categoria    FOREIGN KEY (categoria_id)
        REFERENCES categorias (categoria_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_precio_positivo  CHECK (precio_venta    > 0),
    CONSTRAINT chk_costo_positivo   CHECK (costo_unitario  > 0),
    CONSTRAINT chk_stock_positivo   CHECK (stock          >= 0)
);

-- 5. ventas
CREATE TABLE ventas (
    venta_id   INT  NOT NULL AUTO_INCREMENT,
    fecha      DATE NOT NULL,
    cliente_id INT  NOT NULL,
    CONSTRAINT pk_ventas          PRIMARY KEY (venta_id),
    CONSTRAINT fk_ventas_clientes FOREIGN KEY (cliente_id)
        REFERENCES clientes (cliente_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 6. detalle_ventas
CREATE TABLE detalle_ventas (
    venta_id        INT           NOT NULL,
    producto_id     INT           NOT NULL,
    cantidad        INT           NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento_pct   DECIMAL(5,2)  NULL DEFAULT 0,
    CONSTRAINT pk_detalle        PRIMARY KEY (venta_id, producto_id),
    CONSTRAINT fk_det_venta      FOREIGN KEY (venta_id)
        REFERENCES ventas    (venta_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_det_producto   FOREIGN KEY (producto_id)
        REFERENCES productos (producto_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_cantidad_positiva CHECK (cantidad > 0),
    CONSTRAINT chk_descuento_rango   CHECK (descuento_pct BETWEEN 0 AND 100)
);

-- 7. proveedor_producto
CREATE TABLE proveedor_producto (
    proveedor_id        INT           NOT NULL,
    producto_id         INT           NOT NULL,
    precio_compra       DECIMAL(10,2) NOT NULL,
    plazo_entrega_dias  INT           NULL,
    proveedor_principal TINYINT(1)    NOT NULL DEFAULT 0,
    CONSTRAINT pk_prov_prod      PRIMARY KEY (proveedor_id, producto_id),
    CONSTRAINT fk_pp_proveedor   FOREIGN KEY (proveedor_id)
        REFERENCES proveedores (proveedor_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pp_producto    FOREIGN KEY (producto_id)
        REFERENCES productos   (producto_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- 8. despachos
CREATE TABLE despachos (
    despacho_id            INT          NOT NULL AUTO_INCREMENT,
    venta_id               INT          NOT NULL,
    direccion_entrega      VARCHAR(200) NOT NULL,
    fecha_despacho         DATE         NULL,
    fecha_entrega_estimada DATE         NULL,
    fecha_entrega_real     DATE         NULL,
    estado                 VARCHAR(20)  NOT NULL DEFAULT 'Pendiente',
    CONSTRAINT pk_despachos        PRIMARY KEY (despacho_id),
    CONSTRAINT uq_despacho_venta   UNIQUE (venta_id),
    CONSTRAINT fk_desp_venta       FOREIGN KEY (venta_id)
        REFERENCES ventas (venta_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_estado_despacho
        CHECK (estado IN ('Pendiente','En tránsito','Entregado','No entregado'))
);

-- 9. devoluciones
CREATE TABLE devoluciones (
    devolucion_id     INT           NOT NULL AUTO_INCREMENT,
    venta_id          INT           NOT NULL,
    producto_id       INT           NOT NULL,
    fecha_devolucion  DATE          NOT NULL,
    cantidad_devuelta INT           NOT NULL,
    motivo            VARCHAR(200)  NULL,
    estado            VARCHAR(20)   NOT NULL DEFAULT 'Pendiente',
    monto_reembolsado DECIMAL(10,2) NULL,
    CONSTRAINT pk_devoluciones   PRIMARY KEY (devolucion_id),
    CONSTRAINT fk_dev_venta      FOREIGN KEY (venta_id)
        REFERENCES ventas    (venta_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_dev_producto   FOREIGN KEY (producto_id)
        REFERENCES productos (producto_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ============================================================
-- Carga de datos
-- Los CSV deben estar en la misma carpeta desde donde ejecutas
-- el comando mysql, o ajusta las rutas absolutas abajo.
-- ============================================================

-- Desactivar FK y checks durante la carga masiva
SET foreign_key_checks = 0;
SET unique_checks      = 0;

-- 1. categorias (20 filas — rápido)
LOAD DATA LOCAL INFILE 'bigdata_categorias.csv'
INTO TABLE categorias
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(categoria_id, nombre_categoria, descripcion, @padre)
SET categoria_padre_id = NULLIF(@padre, '');

SELECT CONCAT('categorias: ', COUNT(*)) AS carga FROM categorias;

-- 2. clientes (8 500 000 filas — ~3-6 min)
ALTER TABLE clientes DISABLE KEYS;
LOAD DATA LOCAL INFILE 'bigdata_clientes.csv'
INTO TABLE clientes
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(cliente_id, nombre, apellido, email, region, segmento, fecha_registro);
ALTER TABLE clientes ENABLE KEYS;

SELECT CONCAT('clientes: ', FORMAT(COUNT(*),0)) AS carga FROM clientes;

-- 3. proveedores (80 filas — rápido)
LOAD DATA LOCAL INFILE 'bigdata_proveedores.csv'
INTO TABLE proveedores
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(proveedor_id, nombre_proveedor, rut, contacto, email, telefono);

SELECT CONCAT('proveedores: ', COUNT(*)) AS carga FROM proveedores;

-- 4. productos (300 filas — rápido)
LOAD DATA LOCAL INFILE 'bigdata_productos.csv'
INTO TABLE productos
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(producto_id, nombre_producto, categoria_id, precio_venta, costo_unitario, stock, activo);

SELECT CONCAT('productos: ', COUNT(*)) AS carga FROM productos;

-- 5. proveedor_producto (~600 filas — rápido)
LOAD DATA LOCAL INFILE 'bigdata_proveedor_producto.csv'
INTO TABLE proveedor_producto
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(proveedor_id, producto_id, precio_compra, plazo_entrega_dias, proveedor_principal);

SELECT CONCAT('proveedor_producto: ', COUNT(*)) AS carga FROM proveedor_producto;

-- 6. ventas (8 750 000 filas — ~4-8 min)
ALTER TABLE ventas DISABLE KEYS;
LOAD DATA LOCAL INFILE 'bigdata_ventas.csv'
INTO TABLE ventas
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(venta_id, fecha, cliente_id);
ALTER TABLE ventas ENABLE KEYS;

SELECT CONCAT('ventas: ', FORMAT(COUNT(*),0)) AS carga FROM ventas;

-- 7. detalle_ventas (~12 000 000 filas — ~6-12 min)
ALTER TABLE detalle_ventas DISABLE KEYS;
LOAD DATA LOCAL INFILE 'bigdata_detalle_ventas.csv'
INTO TABLE detalle_ventas
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(venta_id, producto_id, cantidad, precio_unitario, descuento_pct);
ALTER TABLE detalle_ventas ENABLE KEYS;

SELECT CONCAT('detalle_ventas: ', FORMAT(COUNT(*),0)) AS carga FROM detalle_ventas;

-- 8. despachos (~8 225 000 filas — ~4-8 min)
ALTER TABLE despachos DISABLE KEYS;
LOAD DATA LOCAL INFILE 'bigdata_despachos.csv'
INTO TABLE despachos
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(despacho_id, venta_id, direccion_entrega, fecha_despacho,
 fecha_entrega_estimada, @f_real, estado)
SET fecha_entrega_real = NULLIF(@f_real, '');
ALTER TABLE despachos ENABLE KEYS;

SELECT CONCAT('despachos: ', FORMAT(COUNT(*),0)) AS carga FROM despachos;

-- 9. devoluciones (~437 500 filas — ~1-2 min)
ALTER TABLE devoluciones DISABLE KEYS;
LOAD DATA LOCAL INFILE 'bigdata_devoluciones.csv'
INTO TABLE devoluciones
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(devolucion_id, venta_id, producto_id, fecha_devolucion,
 cantidad_devuelta, motivo, estado, @reembolso)
SET monto_reembolsado = NULLIF(@reembolso, '');
ALTER TABLE devoluciones ENABLE KEYS;

SELECT CONCAT('devoluciones: ', FORMAT(COUNT(*),0)) AS carga FROM devoluciones;

-- Restaurar validaciones
SET foreign_key_checks = 1;
SET unique_checks      = 1;

-- ============================================================
-- Índices de rendimiento (crear DESPUÉS de la carga)
-- ============================================================
CREATE INDEX idx_clientes_region    ON clientes    (region);
CREATE INDEX idx_clientes_segmento  ON clientes    (segmento);
CREATE INDEX idx_ventas_fecha       ON ventas      (fecha);
CREATE INDEX idx_ventas_cliente     ON ventas      (cliente_id);
CREATE INDEX idx_detalle_producto   ON detalle_ventas (producto_id);
CREATE INDEX idx_productos_categoria ON productos  (categoria_id);
CREATE INDEX idx_despachos_estado   ON despachos   (estado);
CREATE INDEX idx_despachos_venta    ON despachos   (venta_id);
CREATE INDEX idx_dev_venta          ON devoluciones (venta_id);

-- ============================================================
-- Verificación final
-- ============================================================
SELECT tabla, FORMAT(filas, 0) AS total_filas FROM (
    SELECT 'categorias'        AS tabla, COUNT(*) AS filas FROM categorias
    UNION ALL
    SELECT 'clientes',                   COUNT(*) FROM clientes
    UNION ALL
    SELECT 'proveedores',                COUNT(*) FROM proveedores
    UNION ALL
    SELECT 'productos',                  COUNT(*) FROM productos
    UNION ALL
    SELECT 'ventas',                     COUNT(*) FROM ventas
    UNION ALL
    SELECT 'detalle_ventas',             COUNT(*) FROM detalle_ventas
    UNION ALL
    SELECT 'proveedor_producto',         COUNT(*) FROM proveedor_producto
    UNION ALL
    SELECT 'despachos',                  COUNT(*) FROM despachos
    UNION ALL
    SELECT 'devoluciones',               COUNT(*) FROM devoluciones
) t;
