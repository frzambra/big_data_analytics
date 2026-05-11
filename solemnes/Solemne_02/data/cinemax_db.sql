-- ============================================================
-- cinemax_db.sql
-- Base de datos CineMax para Solemne 2
-- Big Data y Analytics · Universidad San Sebastián · 2026
--
-- Cargar desde HeidiSQL: Herramientas → Cargar archivo SQL
-- O desde terminal: mysql --local-infile=1 -u root -p < cinemax_db.sql
-- ============================================================

DROP DATABASE IF EXISTS cinemax;
CREATE DATABASE cinemax
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_spanish_ci;
USE cinemax;

-- ============================================================
-- DDL — tablas padre antes que hijas
-- ============================================================

CREATE TABLE generos (
    genero_id INT         NOT NULL AUTO_INCREMENT,
    nombre    VARCHAR(50) NOT NULL,
    CONSTRAINT pk_generos PRIMARY KEY (genero_id)
);

CREATE TABLE peliculas (
    pelicula_id   INT          NOT NULL AUTO_INCREMENT,
    titulo        VARCHAR(100) NOT NULL,
    genero_id     INT          NOT NULL,
    duracion_min  INT          NOT NULL,
    clasificacion VARCHAR(5)   NOT NULL,
    CONSTRAINT pk_peliculas      PRIMARY KEY (pelicula_id),
    CONSTRAINT fk_pel_genero     FOREIGN KEY (genero_id)
        REFERENCES generos(genero_id),
    CONSTRAINT chk_duracion      CHECK (duracion_min > 0),
    CONSTRAINT chk_clasificacion CHECK (clasificacion IN ('TE','G','G14','G18'))
);

CREATE TABLE salas (
    sala_id   INT         NOT NULL AUTO_INCREMENT,
    nombre    VARCHAR(50) NOT NULL,
    capacidad INT         NOT NULL,
    tipo      VARCHAR(5)  NOT NULL,
    CONSTRAINT pk_salas      PRIMARY KEY (sala_id),
    CONSTRAINT chk_capacidad CHECK (capacidad > 0),
    CONSTRAINT chk_tipo      CHECK (tipo IN ('2D','3D','4DX'))
);

CREATE TABLE clientes (
    cliente_id INT          NOT NULL AUTO_INCREMENT,
    nombre     VARCHAR(50)  NOT NULL,
    apellido   VARCHAR(50)  NOT NULL,
    email      VARCHAR(100) NOT NULL,
    segmento   VARCHAR(20)  NOT NULL,
    CONSTRAINT pk_clientes       PRIMARY KEY (cliente_id),
    CONSTRAINT uq_clientes_email UNIQUE (email),
    CONSTRAINT chk_segmento      CHECK (segmento IN ('Regular','VIP'))
);

CREATE TABLE funciones (
    funcion_id  INT  NOT NULL AUTO_INCREMENT,
    pelicula_id INT  NOT NULL,
    sala_id     INT  NOT NULL,
    fecha       DATE NOT NULL,
    hora        TIME NOT NULL,
    precio_base INT  NOT NULL,
    CONSTRAINT pk_funciones    PRIMARY KEY (funcion_id),
    CONSTRAINT fk_fun_pelicula FOREIGN KEY (pelicula_id)
        REFERENCES peliculas(pelicula_id),
    CONSTRAINT fk_fun_sala     FOREIGN KEY (sala_id)
        REFERENCES salas(sala_id),
    CONSTRAINT chk_precio      CHECK (precio_base > 0)
);

CREATE TABLE entradas (
    entrada_id    INT          NOT NULL AUTO_INCREMENT,
    funcion_id    INT          NOT NULL,
    cliente_id    INT          NOT NULL,
    cantidad      INT          NOT NULL,
    descuento_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
    CONSTRAINT pk_entradas    PRIMARY KEY (entrada_id),
    CONSTRAINT fk_ent_funcion FOREIGN KEY (funcion_id)
        REFERENCES funciones(funcion_id),
    CONSTRAINT fk_ent_cliente FOREIGN KEY (cliente_id)
        REFERENCES clientes(cliente_id),
    CONSTRAINT chk_cantidad   CHECK (cantidad > 0),
    CONSTRAINT chk_descuento  CHECK (descuento_pct BETWEEN 0 AND 100)
);

-- ============================================================
-- Datos
-- ============================================================

INSERT INTO generos (nombre) VALUES
    ('Acción'),
    ('Comedia'),
    ('Drama'),
    ('Terror'),
    ('Animación');

-- pelicula_id 9 (La Noche Eterna) no tiene funciones asignadas
INSERT INTO peliculas (titulo, genero_id, duracion_min, clasificacion) VALUES
    ('Guardianes del Cosmos', 1, 130, 'G14'),
    ('La Familia Perfecta',   2,  95, 'TE'),
    ('Sombras del Pasado',    3, 118, 'G'),
    ('El Último Grito',       4, 105, 'G18'),
    ('Mundos Animados',       5,  88, 'TE'),
    ('Ruta Peligrosa',        1, 142, 'G14'),
    ('Entre Nosotros',        2, 102, 'G'),
    ('Voces del Silencio',    3, 126, 'G14'),
    ('La Noche Eterna',       4,  98, 'G18');

INSERT INTO salas (nombre, capacidad, tipo) VALUES
    ('Sala 1',        150, '2D'),
    ('Sala 2',        120, '3D'),
    ('Sala Premium',   80, '4DX');

INSERT INTO clientes (nombre, apellido, email, segmento) VALUES
    ('Ana',       'López',   'ana.lopez@gmail.com',     'VIP'),
    ('Pedro',     'Muñoz',   'pedro.munoz@gmail.com',   'Regular'),
    ('María',     'Silva',   'maria.silva@outlook.com', 'Regular'),
    ('Juan',      'Torres',  'j.torres@gmail.com',      'VIP'),
    ('Camila',    'Reyes',   'c.reyes@gmail.com',       'Regular'),
    ('Diego',     'Herrera', 'diego.h@hotmail.com',     'Regular'),
    ('Valentina', 'Castro',  'v.castro@gmail.com',      'VIP'),
    ('Felipe',    'Morales', 'f.morales@yahoo.com',     'Regular'),
    ('Isabella',  'Rojas',   'i.rojas@gmail.com',       'Regular'),
    ('Sebastián', 'Fuentes', 's.fuentes@gmail.com',     'VIP');

-- funcion_id: pelicula_id, sala_id, fecha, hora, precio_base
INSERT INTO funciones (pelicula_id, sala_id, fecha, hora, precio_base) VALUES
    (1, 1, '2026-04-15', '16:00',  6500),  --  1: Guardianes, Sala 1
    (1, 2, '2026-04-15', '19:30',  8000),  --  2: Guardianes, Sala 2
    (2, 1, '2026-04-16', '14:00',  5500),  --  3: La Familia Perfecta, Sala 1
    (2, 3, '2026-04-16', '20:00', 12000),  --  4: La Familia Perfecta, Sala Premium
    (3, 2, '2026-04-18', '18:00',  7000),  --  5: Sombras del Pasado, Sala 2
    (4, 1, '2026-04-19', '21:00',  6500),  --  6: El Último Grito, Sala 1
    (5, 1, '2026-04-20', '11:00',  5500),  --  7: Mundos Animados, Sala 1
    (6, 3, '2026-04-22', '19:00', 12000),  --  8: Ruta Peligrosa, Sala Premium
    (1, 1, '2026-04-25', '17:00',  6500),  --  9: Guardianes, Sala 1 (2ª fecha)
    (3, 2, '2026-04-26', '15:00',  7000),  -- 10: Sombras del Pasado, Sala 2 (2ª fecha)
    (7, 1, '2026-05-01', '16:30',  5500),  -- 11: Entre Nosotros, Sala 1
    (8, 2, '2026-05-02', '19:00',  7500);  -- 12: Voces del Silencio, Sala 2

-- funcion_id, cliente_id, cantidad, descuento_pct
INSERT INTO entradas (funcion_id, cliente_id, cantidad, descuento_pct) VALUES
    ( 1,  1, 2, 10.00),   -- Ana   : 2×6500×0.90 = 11.700
    ( 1,  3, 3,  0.00),   -- María : 3×6500×1.00 = 19.500
    ( 2,  4, 2, 15.00),   -- Juan  : 2×8000×0.85 = 13.600
    ( 2,  7, 4, 10.00),   -- Valentina: 4×8000×0.90 = 28.800
    ( 3,  5, 2,  0.00),   -- Camila: 2×5500 = 11.000
    ( 3,  8, 1,  5.00),   -- Felipe: 1×5500×0.95 = 5.225
    ( 4,  1, 2, 20.00),   -- Ana   : 2×12000×0.80 = 19.200
    ( 4, 10, 3, 15.00),   -- Sebastián: 3×12000×0.85 = 30.600
    ( 5,  2, 2,  0.00),   -- Pedro : 2×7000 = 14.000
    ( 5,  6, 3, 10.00),   -- Diego : 3×7000×0.90 = 18.900
    ( 6,  9, 2,  0.00),   -- Isabella: 2×6500 = 13.000
    ( 6,  4, 3,  5.00),   -- Juan  : 3×6500×0.95 = 18.525
    ( 7,  3, 4,  0.00),   -- María : 4×5500 = 22.000
    ( 7,  1, 2, 10.00),   -- Ana   : 2×5500×0.90 = 9.900
    ( 8, 10, 2, 20.00),   -- Sebastián: 2×12000×0.80 = 19.200
    ( 8,  7, 1,  0.00),   -- Valentina: 1×12000 = 12.000
    ( 9,  2, 3,  0.00),   -- Pedro : 3×6500 = 19.500
    ( 9,  5, 2,  5.00),   -- Camila: 2×6500×0.95 = 12.350
    (10,  6, 2,  0.00),   -- Diego : 2×7000 = 14.000
    (10,  3, 3, 10.00),   -- María : 3×7000×0.90 = 18.900
    (11,  8, 2,  0.00),   -- Felipe: 2×5500 = 11.000
    (11,  9, 3,  5.00),   -- Isabella: 3×5500×0.95 = 15.675
    (12,  4, 2, 15.00),   -- Juan  : 2×7500×0.85 = 12.750
    (12,  1, 1, 10.00);   -- Ana   : 1×7500×0.90 = 6.750
