"""
generate_big_data.py
--------------------
Genera los archivos CSV de gran escala para el modelo TechStyle (W05 — 9 tablas).

Tablas y volúmenes:
  Static (pequeñas, no aleatorias):
    bigdata_categorias.csv        20 filas
    bigdata_proveedores.csv       80 filas
    bigdata_productos.csv        300 filas
    bigdata_proveedor_producto.csv  ~600 filas

  Grandes (generadas aleatoriamente):
    bigdata_clientes.csv       8 500 000 filas
    bigdata_ventas.csv         8 750 000 filas
    bigdata_detalle_ventas.csv ~12 250 000 filas  (avg 1.4 ítems por venta)
    bigdata_despachos.csv      ~8 225 000 filas   (~94 % de las ventas)
    bigdata_devoluciones.csv   ~437 500 filas     (~5 % de las ventas)

Requisitos:
    pip install numpy pandas

Uso:
    python generate_big_data.py

Tiempo estimado: 4–8 minutos en un laptop moderno.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import time

SEED = 42
rng  = np.random.default_rng(SEED)

OUT_DIR = Path(__file__).parent
CHUNK   = 500_000   # filas por chunk al escribir

# Volúmenes
N_CLIENTES   = 8_500_000
N_VENTAS     = 8_750_000
TASA_DESPACHO    = 0.94    # 94 % de ventas tienen despacho
TASA_DEVOLUCION  = 0.05    # 5 % de ventas tienen devolución

# ─────────────────────────────────────────────────────────────────────────────
# Catálogos chilenos
# ─────────────────────────────────────────────────────────────────────────────
NOMBRES = [
    "Isidora","Daniela","Javiera","Catalina","Valentina","Camila",
    "Fernanda","Sofía","María","Constanza","Gabriela","Francisca",
    "Sebastián","Matías","Felipe","Diego","Andrés","Nicolás",
    "Francisco","Pablo","Martín","Cristóbal","Ignacio","Rodrigo",
    "Carla","Natalia","Paulina","Bárbara","Carolina","Tomás",
    "Vicente","Benjamín","Maximiliano","Alejandro","Ricardo","Claudia",
    "Paola","Andrea","Lorena","Patricia","Jorge","Carlos","Luis",
    "Roberto","Manuel","Eduardo","Fernando","Javier","Miguel","Rafael",
]

APELLIDOS = [
    "González","Muñoz","Rojas","Díaz","Pérez","Soto","Contreras",
    "Silva","Martínez","Sepúlveda","Morales","Torres","Flores",
    "Rivera","Espinoza","Castro","Herrera","Fuentes","Vargas",
    "Ramos","Gutiérrez","Ramírez","Vega","Bravo","Medina",
    "León","Reyes","Ortiz","Pizarro","Carrasco","Tapia","Pinto",
    "Salinas","Núñez","Aguilera","Araya","Campos","Vera","Molina",
    "Valenzuela","Ríos","Sandoval","Figueroa","Orozco","Henríquez",
]

# Regiones con peso proporcional a población
REGIONES_PESOS = [
    ("Metropolitana",        0.40),
    ("Valparaíso",           0.11),
    ("Biobío",               0.10),
    ("La Araucanía",         0.05),
    ("Maule",                0.05),
    ("O'Higgins",            0.05),
    ("Los Lagos",            0.04),
    ("Antofagasta",          0.04),
    ("Coquimbo",             0.04),
    ("Atacama",              0.02),
    ("Tarapacá",             0.02),
    ("Los Ríos",             0.02),
    ("Ñuble",                0.02),
    ("Arica y Parinacota",   0.01),
    ("Magallanes",           0.01),
    ("Aysén",                0.01),
    ("Isla de Pascua",       0.01),
]
REGIONES = [r for r, _ in REGIONES_PESOS]
REG_P    = np.array([p for _, p in REGIONES_PESOS])
REG_P   /= REG_P.sum()

SEGMENTOS    = ["Premium","Estándar","Básico"]
SEG_PESOS    = np.array([0.20, 0.35, 0.45])

DESCUENTOS   = np.array([0, 0, 0, 0, 0, 5, 10, 15, 20])

START_DATE   = np.datetime64("2019-01-01")
END_DATE     = np.datetime64("2024-12-31")
DATE_RANGE   = int((END_DATE - START_DATE).astype(int))


# ─────────────────────────────────────────────────────────────────────────────
# Tabla 1: categorias  (estática — 20 filas)
# ─────────────────────────────────────────────────────────────────────────────
CATEGORIAS = [
    # id, nombre,                  descripcion,                        padre
    ( 1, "Electrónica",           "Dispositivos y tecnología",        None),
    ( 2, "Audio",                 "Auriculares, parlantes y más",        1),
    ( 3, "Computación",           "Periféricos y accesorios PC",         1),
    ( 4, "Fotografía",            "Cámaras y accesorios",               1),
    ( 5, "Ropa",                  "Indumentaria en general",           None),
    ( 6, "Ropa Mujer",            "Prendas femeninas",                   5),
    ( 7, "Ropa Hombre",           "Prendas masculinas",                  5),
    ( 8, "Calzado",               "Zapatos y zapatillas",                5),
    ( 9, "Hogar",                 "Artículos para el hogar",           None),
    (10, "Cocina",                "Utensilios y electrodomésticos",      9),
    (11, "Dormitorio",            "Ropa de cama y almohadas",            9),
    (12, "Decoración",            "Lámparas, cuadros y más",             9),
    (13, "Accesorios",            "Bolsos, lentes y bisutería",        None),
    (14, "Bolsos y Mochilas",     "Mochilas, carteras y maletines",     13),
    (15, "Joyería y Bisutería",   "Collares, pulseras y relojes",       13),
    (16, "Lentes",                "Lentes de sol y de lectura",          13),
    (17, "Deportes",              "Artículos deportivos",              None),
    (18, "Fitness",               "Ropa y equipos de gym",              17),
    (19, "Outdoor",               "Camping y aventura",                  17),
    (20, "Natación",              "Trajes de baño y accesorios",         17),
]


# ─────────────────────────────────────────────────────────────────────────────
# Tabla 2: proveedores  (estática — 80 filas)
# ─────────────────────────────────────────────────────────────────────────────
_PROV_NOMBRES = [
    "TechImport SpA","DistriElec Ltda","ProAudio Chile","MegaStock SA",
    "FashionSur Ltda","TextilChile SpA","ModaImport SA","CalzaChile Ltda",
    "HomePlus SpA","CocinaTotal SA","BedLinens Chile","DecoHogar Ltda",
    "BagWorld SpA","AccessChile SA","LensCenter Ltda","JoyerChile SpA",
    "SportMax SA","FitGear SpA","OutdoorChile Ltda","SwimPro SA",
    "GlobalTech SpA","AsiaImport Ltda","EuroStyle SA","LatamDist SpA",
    "NorteGrande SA","SurDistrib Ltda","CentroLogist SpA","PacíficoTrade SA",
    "AndesImport Ltda","PatagoniaGoods SA","ConexiónNorte SpA","TradeSur Ltda",
    "ChileExport SA","AndeanProducts SpA","SurTech Ltda","BioDistrib SA",
    "AraucaníaGoods SpA","LagosImport Ltda","ValpoTrade SA","MaculStock SpA",
    "ProveElite SA","FastLogist SpA","PremiumDist Ltda","StockMaster SA",
    "ImportCentro SpA","Distribuidora JM Ltda","Comercial BL SA","Proveedor PX SpA",
    "LogiChile SA","TransAndina Ltda","NuevoMundo SpA","GlobalSource SA",
    "AltaCalidad Ltda","MegaProv SpA","DataImport SA","TechSource Ltda",
    "FashionHub SpA","TrendDist SA","StyleSource Ltda","EliteGoods SpA",
    "HomeSource SA","KitchenPro Ltda","TextilMundo SpA","ModaGlobal SA",
    "SportSource Ltda","FitnessPro SpA","CampingTech SA","AquaSport Ltda",
    "CelularMundo SpA","TechParts SA","AudioSource Ltda","CompuDist SpA",
    "CameraChile SA","ClickImport Ltda","MochilaWorld SpA","BagSource SA",
    "WatchDist Ltda","JewelChile SpA","SunGlass SA","ReadLens Ltda",
]

PROVEEDORES = []
rng_prov = np.random.default_rng(1)
for i, nombre in enumerate(_PROV_NOMBRES, start=1):
    rut_num  = rng_prov.integers(10_000_000, 99_999_999)
    rut_dv   = rng_prov.choice(list("0123456789K"))
    rut      = f"{rut_num:,}".replace(",", ".") + f"-{rut_dv}"
    contacto = f"{NOMBRES[i % len(NOMBRES)]} {APELLIDOS[i % len(APELLIDOS)]}"
    email    = f"contacto@{nombre.lower().replace(' ','').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')[:20]}.cl"
    fono     = f"+56 9 {rng_prov.integers(10000000,99999999)}"
    PROVEEDORES.append((i, nombre, rut, contacto, email, fono))


# ─────────────────────────────────────────────────────────────────────────────
# Tabla 3: productos  (estática — 300 filas)
# Distribuidos entre 20 categorías hoja
# ─────────────────────────────────────────────────────────────────────────────
_PRODUCTOS_BASE = [
    # (nombre, cat_id, precio_venta, costo_unitario)
    # Audio (2)
    ("Audífonos Bluetooth Pro",2,54990,22000),("Audífonos In-Ear",2,19990,7000),
    ("Parlante Portátil 10W",2,39990,15000),("Parlante Bluetooth 30W",2,79990,32000),
    ("Soundbar 2.1",2,129990,55000),("Micrófono USB",2,44990,18000),
    ("Audífonos Gamer",2,64990,26000),("Barra de Sonido TV",2,99990,42000),
    ("Audífonos Noise Cancel",2,149990,65000),("Sistema de Audio 5.1",2,199990,85000),
    # Computación (3)
    ("Mouse Inalámbrico",3,24990,9000),("Teclado Mecánico RGB",3,79990,32000),
    ("Monitor 24 FHD",3,139990,68000),("Webcam HD 1080p",3,39990,16000),
    ("Disco Duro 1TB USB",3,54990,22000),("SSD Externo 500GB",3,69990,28000),
    ("Hub USB-C 7en1",3,34990,13000),("Mousepad XL",3,14990,5000),
    ("Soporte Laptop Ajustable",3,29990,11000),("Luz LED Ring 26cm",3,44990,17000),
    ("Router WiFi 6",3,89990,38000),("Switch 8 puertos",3,49990,20000),
    # Fotografía (4)
    ("Cámara DSLR Básica",4,299990,130000),("Lente 50mm f/1.8",4,99990,42000),
    ("Trípode Aluminio",4,34990,13000),("Bolso Cámara",4,24990,9000),
    ("Tarjeta SD 128GB",4,19990,7000),("Flash Externo",4,59990,24000),
    # Ropa Mujer (6)
    ("Polera Algodón Mujer",6,12990,4200),("Jeans Slim Mujer",6,29990,11000),
    ("Parka Impermeable Mujer",6,59990,23000),("Vestido Casual",6,24990,9000),
    ("Blusa Formal",6,19990,7000),("Leggings Deportivos",6,18990,6500),
    ("Chaqueta Denim Mujer",6,44990,18000),("Falda Midi",6,22990,8000),
    ("Poleron Oversized",6,27990,10000),("Pijama Algodón Mujer",6,19990,7000),
    # Ropa Hombre (7)
    ("Polera Básica Hombre",7,11990,4000),("Jeans Slim Hombre",7,27990,10000),
    ("Camisa Oxford",7,24990,9000),("Chaqueta Cuero Sintético",7,69990,28000),
    ("Bermuda Cargo",7,19990,7000),("Poleron Canguro",7,24990,9000),
    ("Pantalón de Buzo",7,17990,6000),("Camiseta Deportiva",7,14990,5000),
    ("Parka Técnica Hombre",7,64990,26000),("Pijama Hombre",7,18990,6500),
    # Calzado (8)
    ("Zapatillas Running",8,49990,19000),("Zapatillas Urbanas",8,39990,15000),
    ("Zapatos de Cuero",8,59990,24000),("Botas Invierno",8,69990,28000),
    ("Sandalias Verano",8,19990,7000),("Zapatillas Trekking",8,54990,22000),
    ("Mocasines",8,44990,18000),("Pantuflas Antideslizantes",8,12990,4200),
    # Cocina (10)
    ("Sartén Antiadherente 28cm",10,19990,7000),("Set Ollas 5 piezas",10,49990,20000),
    ("Cuchillo Chef 20cm",10,24990,9000),("Tabla de Cortar Bambú",10,12990,4200),
    ("Licuadora 1000W",10,34990,13000),("Cafetera Express",10,79990,32000),
    ("Tostadora 4 Ranuras",10,29990,11000),("Hervidor Eléctrico",10,19990,7000),
    ("Jarra Filtro 2.5L",10,34990,13000),("Batidora de Mano",10,24990,9000),
    ("Air Fryer 4L",10,69990,28000),("Olla a Presión 6L",10,44990,18000),
    # Dormitorio (11)
    ("Juego de Camas 2 Plazas",11,29990,11000),("Almohada Viscoelástica",11,24990,9000),
    ("Duvet 2P Invierno",11,49990,20000),("Set Sábanas 2P",11,19990,7000),
    ("Cubre Cama Estampado",11,34990,13000),("Almohada Cervical",11,29990,11000),
    # Decoración (12)
    ("Lámpara LED Escritorio",12,24990,9000),("Cojín Decorativo",12,11990,3500),
    ("Set Toallas x3",12,18990,6500),("Alfombra 120x80",12,44990,18000),
    ("Marco Fotos 30x40",12,9990,3000),("Vela Aromática",12,7990,2500),
    ("Macetero Cerámica",12,14990,5000),("Cuadro Decorativo",12,19990,7000),
    # Bolsos y Mochilas (14)
    ("Mochila Urban 20L",14,39990,14000),("Mochila Trekking 45L",14,69990,28000),
    ("Maletín Laptop 15\"",14,34990,13000),("Cartera Cuero Mujer",14,49990,20000),
    ("Bolso Cruzado",14,24990,9000),("Mochila Portátil Slim",14,44990,18000),
    # Joyería y Bisutería (15)
    ("Reloj Digital Deportivo",15,49990,16000),("Reloj Análogo Clásico",15,69990,28000),
    ("Pulsera Silicona Fit",15,7990,1500),("Collar Acero Inox",15,14990,5000),
    ("Aros Plata 925",15,12990,4200),("Set Anillos Dorados",15,9990,3000),
    # Lentes (16)
    ("Gafas de Sol UV400",16,29990,9000),("Lentes de Lectura +2.0",16,12990,3500),
    ("Lentes Gaming Anti-azul",16,24990,8000),("Gafas Deportivas",16,19990,6500),
    # Fitness (18)
    ("Mancuernas 5kg par",18,19990,7000),("Banda Elástica Set 5",18,9990,3000),
    ("Esterilla Yoga 6mm",18,14990,5000),("Cuerda para Saltar Pro",18,7990,2500),
    ("Guantes Gym",18,11990,3500),("Botella Gym 750ml",18,9990,3000),
    ("Ropa Deportiva Mujer Set",18,29990,11000),("Camiseta Técnica Hombre",18,14990,5000),
    ("Cinturón Lumbar",18,19990,7000),("Foam Roller",18,17990,6000),
    # Outdoor (19)
    ("Carpa 2 Personas",19,79990,32000),("Sleeping Bag -5°C",19,59990,24000),
    ("Linterna Frontal LED",19,14990,5000),("Navaja Multiusos",19,24990,9000),
    ("Bastones Trekking par",19,34990,13000),("Impermeable Poncho",19,19990,7000),
    # Natación (20)
    ("Traje de Baño Mujer",20,19990,7000),("Short Baño Hombre",20,14990,5000),
    ("Antiparras UV",20,9990,3000),("Gorra Natación Silicona",20,7990,2500),
    ("Snorkel Set",20,19990,7000),("Aletas Buceo",20,24990,9000),
]

PRODUCTOS = []
for i, (nombre, cat_id, precio, costo) in enumerate(_PRODUCTOS_BASE, start=1):
    stock = int(rng.integers(10, 500))
    activo = 1
    PRODUCTOS.append((i, nombre, cat_id, precio, costo, stock, activo))

# Vectores para uso en generación de ventas
PROD_IDS    = np.array([p[0] for p in PRODUCTOS])
PROD_PRICES = np.array([p[3] for p in PRODUCTOS])

# ─────────────────────────────────────────────────────────────────────────────
# Tabla 4: proveedor_producto  (estática — ~600 filas)
# Cada producto tiene entre 2 y 5 proveedores; uno es principal
# ─────────────────────────────────────────────────────────────────────────────
_rng_pp = np.random.default_rng(2)
PROV_PROD = []
for prod in PRODUCTOS:
    prod_id = prod[0]
    precio_venta = prod[3]
    n_provs = int(_rng_pp.integers(2, 6))
    prov_ids = _rng_pp.choice(len(PROVEEDORES), size=n_provs, replace=False) + 1
    for j, prov_id in enumerate(prov_ids):
        precio_compra = round(float(precio_venta) * _rng_pp.uniform(0.45, 0.70), 2)
        plazo = int(_rng_pp.integers(3, 31))
        principal = 1 if j == 0 else 0
        PROV_PROD.append((int(prov_id), prod_id, precio_compra, plazo, principal))


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def random_dates(n: int) -> np.ndarray:
    days = rng.integers(0, DATE_RANGE + 1, size=n)
    return (START_DATE + days.astype("timedelta64[D]")).astype(str)


def write_csv_chunked(path: Path, header: str, chunk_gen, total: int):
    written = 0
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        for chunk_lines in chunk_gen:
            f.write(chunk_lines)
            written += chunk_lines.count("\n")
            print(f"  {written:>12,} / {total:,}  ({written/total*100:.1f}%)", end="\r")
    print(f"  {written:>12,} / {total:,}  (100.0%) — listo")


# ─────────────────────────────────────────────────────────────────────────────
# Generadores de tablas estáticas
# ─────────────────────────────────────────────────────────────────────────────
def gen_categorias():
    path = OUT_DIR / "bigdata_categorias.csv"
    with open(path, "w", encoding="utf-8") as f:
        f.write("categoria_id,nombre_categoria,descripcion,categoria_padre_id\n")
        for cat_id, nombre, desc, padre in CATEGORIAS:
            padre_str = "" if padre is None else str(padre)
            f.write(f'{cat_id},"{nombre}","{desc}",{padre_str}\n')
    print(f"  {len(CATEGORIAS)} categorías → {path.name}")


def gen_proveedores():
    path = OUT_DIR / "bigdata_proveedores.csv"
    with open(path, "w", encoding="utf-8") as f:
        f.write("proveedor_id,nombre_proveedor,rut,contacto,email,telefono\n")
        for row in PROVEEDORES:
            f.write(",".join(str(x) for x in row) + "\n")
    print(f"  {len(PROVEEDORES)} proveedores → {path.name}")


def gen_productos():
    path = OUT_DIR / "bigdata_productos.csv"
    with open(path, "w", encoding="utf-8") as f:
        f.write("producto_id,nombre_producto,categoria_id,precio_venta,costo_unitario,stock,activo\n")
        for row in PRODUCTOS:
            prod_id, nombre, cat_id, precio, costo, stock, activo = row
            f.write(f'{prod_id},"{nombre}",{cat_id},{precio},{costo},{stock},{activo}\n')
    print(f"  {len(PRODUCTOS)} productos → {path.name}")


def gen_proveedor_producto():
    path = OUT_DIR / "bigdata_proveedor_producto.csv"
    with open(path, "w", encoding="utf-8") as f:
        f.write("proveedor_id,producto_id,precio_compra,plazo_entrega_dias,proveedor_principal\n")
        for row in PROV_PROD:
            f.write(",".join(str(x) for x in row) + "\n")
    print(f"  {len(PROV_PROD)} relaciones proveedor-producto → {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Generadores de tablas grandes
# ─────────────────────────────────────────────────────────────────────────────

# ---------- clientes ----------
def _clientes_chunk(start_id: int, n: int) -> str:
    ids          = np.arange(start_id, start_id + n)
    nom_idx      = rng.integers(0, len(NOMBRES),   size=n)
    ape_idx      = rng.integers(0, len(APELLIDOS), size=n)
    reg_idx      = rng.choice(len(REGIONES), size=n, p=REG_P)
    seg_idx      = rng.choice(len(SEGMENTOS), size=n, p=SEG_PESOS)
    fechas       = random_dates(n)
    lines = []
    for i in range(n):
        nombre   = NOMBRES[nom_idx[i]]
        apellido = APELLIDOS[ape_idx[i]]
        region   = REGIONES[reg_idx[i]]
        segmento = SEGMENTOS[seg_idx[i]]
        email    = f"{nombre.lower().replace(' ','')}.{apellido.lower().replace(' ','')}{ids[i]}@gmail.com"
        lines.append(f"{ids[i]},{nombre},{apellido},{email},{region},{segmento},{fechas[i]}\n")
    return "".join(lines)

def gen_clientes():
    path = OUT_DIR / "bigdata_clientes.csv"
    header = "cliente_id,nombre,apellido,email,region,segmento,fecha_registro"
    print(f"\nGenerando clientes ({N_CLIENTES:,} filas)...")
    def chunks():
        start, rem = 1, N_CLIENTES
        while rem > 0:
            size = min(CHUNK, rem)
            yield _clientes_chunk(start, size)
            start += size; rem -= size
    write_csv_chunked(path, header, chunks(), N_CLIENTES)
    print(f"  → {path.name}")


# ---------- ventas ----------
def _ventas_chunk(start_id: int, n: int) -> str:
    ids        = np.arange(start_id, start_id + n)
    fechas     = random_dates(n)
    cliente_ids = rng.integers(1, N_CLIENTES + 1, size=n)
    lines = [f"{ids[i]},{fechas[i]},{cliente_ids[i]}\n" for i in range(n)]
    return "".join(lines)

def gen_ventas():
    path = OUT_DIR / "bigdata_ventas.csv"
    header = "venta_id,fecha,cliente_id"
    print(f"\nGenerando ventas ({N_VENTAS:,} filas)...")
    def chunks():
        start, rem = 1, N_VENTAS
        while rem > 0:
            size = min(CHUNK, rem)
            yield _ventas_chunk(start, size)
            start += size; rem -= size
    write_csv_chunked(path, header, chunks(), N_VENTAS)
    print(f"  → {path.name}")


# ---------- detalle_ventas ----------
# Cada venta tiene 1–3 ítems distintos (avg ~1.4)
# Generamos detalle por chunks de ventas
DETALLE_CHUNK = 200_000   # ventas a procesar por vez

def _detalle_chunk(venta_start: int, n_ventas: int):
    """Genera detalles para n_ventas ventas a partir de venta_start."""
    # Número de ítems por venta: 1 con prob 0.55, 2 con prob 0.30, 3 con prob 0.15
    n_items = rng.choice([1, 2, 3], size=n_ventas, p=[0.55, 0.30, 0.15])
    lines   = []
    for v in range(n_ventas):
        venta_id = venta_start + v
        n        = n_items[v]
        # Elegir n productos distintos para esta venta
        prod_idx = rng.choice(len(PROD_IDS), size=n, replace=False)
        for idx in prod_idx:
            prod_id    = int(PROD_IDS[idx])
            precio     = int(PROD_PRICES[idx])
            cantidad   = int(rng.integers(1, 6))
            desc       = int(rng.choice(DESCUENTOS))
            lines.append(f"{venta_id},{prod_id},{cantidad},{precio},{desc}\n")
    return "".join(lines), int(n_items.sum())

def gen_detalle_ventas():
    path = OUT_DIR / "bigdata_detalle_ventas.csv"
    header = "venta_id,producto_id,cantidad,precio_unitario,descuento_pct"
    # Estimación: avg 1.4 ítems × 8.75M ventas ≈ 12.25M filas
    total_est = int(N_VENTAS * 1.4)
    print(f"\nGenerando detalle_ventas (~{total_est:,} filas estimadas)...")
    written = 0
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        start, rem = 1, N_VENTAS
        while rem > 0:
            size = min(DETALLE_CHUNK, rem)
            chunk_text, n_rows = _detalle_chunk(start, size)
            f.write(chunk_text)
            written += n_rows
            print(f"  ventas procesadas: {start+size-1:>10,}/{N_VENTAS:,}  "
                  f"({(start+size-1)/N_VENTAS*100:.1f}%)  filas={written:,}", end="\r")
            start += size; rem -= size
    print(f"  {written:,} filas generadas — listo")
    print(f"  → {path.name}")
    return written


# ---------- despachos ----------
ESTADOS_DESPACHO = ["Pendiente","En tránsito","Entregado","Entregado","Entregado","No entregado"]
COMUNAS = [
    "Santiago","Providencia","Las Condes","Maipú","Puente Alto","La Florida",
    "San Bernardo","Viña del Mar","Valparaíso","Concepción","Temuco","Antofagasta",
    "Rancagua","Talca","Puerto Montt","Arica","Iquique","Coquimbo","Calama","Osorno",
]

def _despachos_chunk(start_despacho: int, venta_start: int, n: int) -> str:
    despacho_ids = np.arange(start_despacho, start_despacho + n)
    venta_ids    = np.arange(venta_start,    venta_start    + n)
    fecha_desp   = random_dates(n)
    estado_idx   = rng.integers(0, len(ESTADOS_DESPACHO), size=n)
    comuna_idx   = rng.integers(0, len(COMUNAS), size=n)
    lines = []
    for i in range(n):
        estado = ESTADOS_DESPACHO[estado_idx[i]]
        dir_   = f"Calle {rng.integers(1,999)} N° {rng.integers(1,9999)}, {COMUNAS[comuna_idx[i]]}"
        # fecha_entrega_estimada = despacho + 3-7 días
        est_days  = int(rng.integers(3, 8))
        real_days = int(rng.integers(3, 10)) if estado in ("Entregado","No entregado") else None
        f_est  = str(np.datetime64(fecha_desp[i]) + np.timedelta64(est_days, "D"))
        f_real = str(np.datetime64(fecha_desp[i]) + np.timedelta64(real_days, "D")) if real_days else ""
        lines.append(f"{despacho_ids[i]},{venta_ids[i]},\"{dir_}\",{fecha_desp[i]},{f_est},{f_real},{estado}\n")
    return "".join(lines)

def gen_despachos():
    n_despachos = int(N_VENTAS * TASA_DESPACHO)
    path = OUT_DIR / "bigdata_despachos.csv"
    header = "despacho_id,venta_id,direccion_entrega,fecha_despacho,fecha_entrega_estimada,fecha_entrega_real,estado"
    print(f"\nGenerando despachos ({n_despachos:,} filas)...")
    def chunks():
        d_start, v_start, rem = 1, 1, n_despachos
        while rem > 0:
            size = min(CHUNK, rem)
            yield _despachos_chunk(d_start, v_start, size)
            d_start += size; v_start += size; rem -= size
    write_csv_chunked(path, header, chunks(), n_despachos)
    print(f"  → {path.name}")


# ---------- devoluciones ----------
MOTIVOS = [
    "Producto dañado","Talla incorrecta","No era lo esperado",
    "Llegó tarde","Producto incompleto","Error en el pedido",
    "Calidad inferior a la esperada","Cambio de opinión",
]
ESTADOS_DEV = ["Pendiente","Aprobada","Rechazada","Reembolsada"]

def _devoluciones_chunk(start_id: int, venta_start: int, n: int) -> str:
    dev_ids    = np.arange(start_id,    start_id    + n)
    venta_ids  = np.arange(venta_start, venta_start + n)
    fechas     = random_dates(n)
    prod_idx   = rng.integers(0, len(PROD_IDS), size=n)
    motivo_idx = rng.integers(0, len(MOTIVOS), size=n)
    estado_idx = rng.integers(0, len(ESTADOS_DEV), size=n)
    cant       = rng.integers(1, 4, size=n)
    lines = []
    for i in range(n):
        precio     = PROD_PRICES[prod_idx[i]]
        reembolso  = round(float(cant[i]) * float(precio) * 0.9, 2) \
                     if ESTADOS_DEV[estado_idx[i]] == "Reembolsada" else ""
        prod_id    = int(PROD_IDS[prod_idx[i]])
        lines.append(
            f"{dev_ids[i]},{venta_ids[i]},{prod_id},{fechas[i]},"
            f"{cant[i]},\"{MOTIVOS[motivo_idx[i]]}\","
            f"{ESTADOS_DEV[estado_idx[i]]},{reembolso}\n"
        )
    return "".join(lines)

def gen_devoluciones():
    n_dev = int(N_VENTAS * TASA_DEVOLUCION)
    # Ventas con devolución: las últimas n_dev ventas (simplificación pedagógica)
    venta_offset = N_VENTAS - n_dev + 1
    path = OUT_DIR / "bigdata_devoluciones.csv"
    header = "devolucion_id,venta_id,producto_id,fecha_devolucion,cantidad_devuelta,motivo,estado,monto_reembolsado"
    print(f"\nGenerando devoluciones ({n_dev:,} filas)...")
    def chunks():
        d_start, v_start, rem = 1, venta_offset, n_dev
        while rem > 0:
            size = min(CHUNK, rem)
            yield _devoluciones_chunk(d_start, v_start, size)
            d_start += size; v_start += size; rem -= size
    write_csv_chunked(path, header, chunks(), n_dev)
    print(f"  → {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    t0 = time.time()
    print("=" * 60)
    print("  TechStyle — Generador Big Data (9 tablas, esquema W05)")
    print("=" * 60)

    print("\n--- Tablas estáticas ---")
    gen_categorias()
    gen_proveedores()
    gen_productos()
    gen_proveedor_producto()

    print("\n--- Tablas grandes ---")
    gen_clientes()
    gen_ventas()
    n_detalle = gen_detalle_ventas()
    gen_despachos()
    gen_devoluciones()

    elapsed = time.time() - t0
    print(f"\nTiempo total: {elapsed:.1f} s")

    archivos = [
        "bigdata_categorias.csv","bigdata_proveedores.csv",
        "bigdata_productos.csv","bigdata_proveedor_producto.csv",
        "bigdata_clientes.csv","bigdata_ventas.csv",
        "bigdata_detalle_ventas.csv","bigdata_despachos.csv",
        "bigdata_devoluciones.csv",
    ]
    print("\nArchivos generados:")
    total_mb = 0
    for fname in archivos:
        p = OUT_DIR / fname
        if p.exists():
            mb = p.stat().st_size / 1_048_576
            total_mb += mb
            print(f"  {fname:<38} {mb:>8.1f} MB")
    print(f"  {'TOTAL':<38} {total_mb:>8.1f} MB")
    print("\nSiguiente paso: ejecutar load_big_data.sql en MySQL")
