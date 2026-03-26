-- W04 · TechStyle · Modelo Relacional Normalizado
-- Orden: tablas sin FK primero

CREATE TABLE clientes (
    cliente_id      INT           PRIMARY KEY,
    nombre          VARCHAR(50)   NOT NULL,
    apellido        VARCHAR(50)   NOT NULL,
    email           VARCHAR(100)  UNIQUE NOT NULL,
    region          VARCHAR(50)   NOT NULL,
    segmento        VARCHAR(20)   CHECK (segmento IN ('Premium', 'Estándar', 'Básico')),
    fecha_registro  DATE          NOT NULL
);

CREATE TABLE productos (
    producto_id      INT            PRIMARY KEY,
    nombre_producto  VARCHAR(100)   NOT NULL,
    categoria        VARCHAR(50)    NOT NULL,
    precio_venta     DECIMAL(10,2)  NOT NULL CHECK (precio_venta > 0),
    costo_unitario   DECIMAL(10,2)  NOT NULL CHECK (costo_unitario > 0),
    stock            INT            NOT NULL DEFAULT 0
);

CREATE TABLE ventas (
    venta_id    VARCHAR(10)  PRIMARY KEY,
    fecha       DATE         NOT NULL,
    cliente_id  INT          NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
);

CREATE TABLE detalle_ventas (
    venta_id         VARCHAR(10)   NOT NULL,
    producto_id      INT           NOT NULL,
    cantidad         INT           NOT NULL CHECK (cantidad > 0),
    precio_unitario  DECIMAL(10,2) NOT NULL,
    descuento_pct    DECIMAL(5,2)  NOT NULL DEFAULT 0
                                   CHECK (descuento_pct BETWEEN 0 AND 100),
    PRIMARY KEY (venta_id, producto_id),
    FOREIGN KEY (venta_id)   REFERENCES ventas(venta_id),
    FOREIGN KEY (producto_id) REFERENCES productos(producto_id)
);
