"""
Generador de datos sintéticos para TechStyle — Big Data y Analytics
Universidad San Sebastián

Genera los archivos de datos para los laboratorios de la Unidad 1:
  - techstyle_orders.csv        → Lab Semana 1
  - techstyle_customers_dirty.csv → Lab Semana 3
  - oltp_ventas.csv             → Lab Semana 4
  - oltp_clientes.csv           → Lab Semana 4
  - oltp_productos.csv          → Lab Semana 4
"""

import csv
import random
from datetime import datetime, timedelta
import os

random.seed(42)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")

# ─────────────────────────────────────────────────────────
# CATÁLOGO DE PRODUCTOS
# (id, nombre, categoria, costo, precio_venta)
# ─────────────────────────────────────────────────────────
PRODUCTS = [
    # Electrónica
    (1001, "Audífonos Bluetooth",    "Electrónica", 18000,  44990),
    (1002, "Cargador Rápido USB-C",  "Electrónica",  6000,  15990),
    (1003, "Parlante Portátil",      "Electrónica", 25000,  59990),
    (1004, "Mouse Inalámbrico",      "Electrónica",  9000,  24990),
    (1005, "Teclado Mecánico",       "Electrónica", 32000,  79990),
    (1006, 'Monitor 24"',            "Electrónica", 68000, 139990),
    (1007, "Webcam HD",              "Electrónica", 16000,  39990),
    (1008, "Disco Duro Externo 1TB", "Electrónica", 22000,  54990),
    # Ropa
    (2001, "Polera Básica",          "Ropa",  4000,  12990),
    (2002, "Jeans Slim",             "Ropa", 11000,  29990),
    (2003, "Parka Impermeable",      "Ropa", 23000,  59990),
    (2004, "Zapatillas Running",     "Ropa", 19000,  49990),
    (2005, "Poleron Algodón",        "Ropa",  8500,  24990),
    (2006, "Pantalón de Buzo",       "Ropa",  6000,  19990),
    (2007, "Calcetines Pack 3",      "Ropa",  1800,   5990),
    (2008, "Gorra",                  "Ropa",  3500,  11990),
    # Hogar
    (3001, "Sartén Antiadherente",   "Hogar",  7000,  19990),
    (3002, "Juego de Camas 2P",      "Hogar", 11000,  29990),
    (3003, "Organizador Cajones",    "Hogar",  5000,  14990),
    (3004, "Lámpara LED Escritorio", "Hogar",  9000,  24990),
    (3005, "Cojín Decorativo",       "Hogar",  3500,  11990),
    (3006, "Set Toallas x3",         "Hogar",  6500,  18990),
    (3007, "Jarra Filtro Agua",      "Hogar", 13000,  34990),
    (3008, "Alfombra 120x80",        "Hogar", 18000,  44990),
    # Accesorios
    (4001, "Mochila Urban",          "Accesorios", 14000,  39990),
    (4002, "Billetera Cuero",        "Accesorios",  6000,  19990),
    (4003, "Gafas de Sol",           "Accesorios",  9000,  29990),
    (4004, "Reloj Digital",          "Accesorios", 16000,  49990),
    (4005, "Pulsera Silicona",       "Accesorios",  1500,   7990),
    (4006, "Porta Notebook",         "Accesorios",  8000,  24990),
    (4007, "Paraguas Compacto",      "Accesorios",  4500,  14990),
    (4008, "Lentes de Lectura",      "Accesorios",  3500,  12990),
]

REGIONS = ["RM", "Valparaíso", "Biobío", "Maule", "La Araucanía",
           "Los Lagos", "Antofagasta", "Coquimbo", "O'Higgins"]
REGION_W = [0.45, 0.15, 0.12, 0.07, 0.06, 0.05, 0.04, 0.03, 0.03]

NOMBRES = ["Valentina", "Sofía", "Camila", "Isidora", "Fernanda",
           "Javiera", "Daniela", "Catalina", "María", "Constanza",
           "Martín", "Diego", "Felipe", "Sebastián", "Nicolás",
           "Matías", "Alejandro", "Andrés", "Francisco", "Pablo"]
APELLIDOS = ["González", "Muñoz", "Rojas", "Díaz", "Pérez",
             "Soto", "Contreras", "Silva", "Martínez", "Sepúlveda",
             "Morales", "Torres", "Fuentes", "Vargas", "Flores",
             "Herrera", "Castro", "Gutiérrez", "Ramos", "Espinoza"]

CANALES = ["Web", "App móvil", "App móvil", "Web"]  # más peso a app


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def random_phone():
    return f"9{random.randint(10000000, 99999999)}"


# ─────────────────────────────────────────────────────────
# LAB SEMANA 1 — techstyle_orders.csv
# ─────────────────────────────────────────────────────────
def generate_orders(n_customers=200, n_orders=700):
    """Genera pedidos con líneas de detalle para análisis de categorías."""
    start = datetime(2023, 1, 1)
    end   = datetime(2023, 12, 31)

    # Assign customer regions
    customer_regions = {
        cid: random.choices(REGIONS, weights=REGION_W)[0]
        for cid in range(1, n_customers + 1)
    }
    customer_channels = {
        cid: random.choice(CANALES)
        for cid in range(1, n_customers + 1)
    }

    # Category weights by month (Electrónica sube en nov-dic, Ropa en may-ago)
    def product_weights(month):
        if month in [11, 12]:          # Black Friday / Navidad
            return [0.38, 0.22, 0.22, 0.18]  # E, R, H, A
        elif month in [5, 6, 7, 8]:    # Invierno → más Ropa y Hogar
            return [0.22, 0.32, 0.28, 0.18]
        else:
            return [0.28, 0.28, 0.26, 0.18]

    rows = []
    order_id = 10001
    for _ in range(n_orders):
        fecha = random_date(start, end)
        cliente_id = random.randint(1, n_customers)
        region = customer_regions[cliente_id]
        canal  = customer_channels[cliente_id]
        n_items = random.choices([1, 2, 3, 4], weights=[0.50, 0.30, 0.15, 0.05])[0]

        # pick category distribution for this month
        cat_weights = product_weights(fecha.month)
        cat_pool = (
            [p for p in PRODUCTS if p[2] == "Electrónica"] * int(cat_weights[0] * 100) +
            [p for p in PRODUCTS if p[2] == "Ropa"]        * int(cat_weights[1] * 100) +
            [p for p in PRODUCTS if p[2] == "Hogar"]       * int(cat_weights[2] * 100) +
            [p for p in PRODUCTS if p[2] == "Accesorios"]  * int(cat_weights[3] * 100)
        )

        selected = random.sample(cat_pool, min(n_items, len(cat_pool)))
        for prod in selected:
            pid, nombre, cat, costo, precio = prod
            cantidad = random.choices([1, 2, 3], weights=[0.70, 0.22, 0.08])[0]
            descuento = random.choices([0, 0.05, 0.10, 0.15, 0.20],
                                       weights=[0.55, 0.15, 0.15, 0.10, 0.05])[0]
            precio_final = round(precio * (1 - descuento))
            venta_neta   = precio_final * cantidad
            margen       = round((precio_final - costo) / precio_final * 100, 1)

            rows.append({
                "order_id":       order_id,
                "fecha":          fecha.strftime("%Y-%m-%d"),
                "mes":            fecha.month,
                "año":            fecha.year,
                "trimestre":      f"T{(fecha.month - 1) // 3 + 1}",
                "cliente_id":     cliente_id,
                "region":         region,
                "canal_venta":    canal,
                "product_id":     pid,
                "nombre_producto": nombre,
                "categoria":      cat,
                "cantidad":       cantidad,
                "precio_unitario": precio_final,
                "descuento_pct":  int(descuento * 100),
                "venta_neta":     venta_neta,
                "margen_pct":     margen,
            })
        order_id += 1

    out_path = os.path.join(OUTPUT_DIR, "techstyle_orders.csv")
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] {out_path}  ({len(rows)} filas)")


# ─────────────────────────────────────────────────────────
# LAB SEMANA 3 — techstyle_customers_dirty.csv
# ─────────────────────────────────────────────────────────
def generate_dirty_customers(n=200):
    """Genera clientes con problemas de calidad de datos intencionales."""
    start_reg = datetime(2020, 1, 1)
    end_reg   = datetime(2023, 12, 31)
    start_nac = datetime(1970, 1, 1)
    end_nac   = datetime(2003, 12, 31)

    rows = []
    phones_used = []

    for i in range(1, n + 1):
        nombre   = random.choice(NOMBRES)
        apellido = random.choice(APELLIDOS)
        region   = random.choices(REGIONS, weights=REGION_W)[0]
        phone    = random_phone()
        phones_used.append(phone)
        fecha_nac = random_date(start_nac, end_nac).strftime("%Y-%m-%d")
        fecha_reg = random_date(start_reg, end_reg).strftime("%Y-%m-%d")
        email_base = f"{nombre.lower()}.{apellido.lower()}@gmail.com"

        row = {
            "id":              i,
            "nombre":          nombre,
            "apellido":        apellido,
            "email":           email_base,
            "telefono":        phone,
            "region":          region,
            "fecha_nacimiento": fecha_nac,
            "fecha_registro":  fecha_reg,
            "segmento":        random.choice(["Premium", "Estándar", "Básico"]),
        }

        # ── Inyectar problemas de calidad ──────────────────────────────
        r = random.random()

        # ~12%: email NULL
        if r < 0.12:
            row["email"] = ""

        # ~8%: email mal formado (sin dominio completo)
        elif r < 0.20:
            row["email"] = f"{nombre.lower()}.{apellido.lower()}@gmail"

        # ~5%: email sin @
        elif r < 0.25:
            row["email"] = f"{nombre.lower()}{apellido.lower()}gmail.com"

        # ~20%: fecha_nacimiento NULL
        if random.random() < 0.20:
            row["fecha_nacimiento"] = ""

        # ~8%: region NULL
        if random.random() < 0.08:
            row["region"] = ""

        # ~6%: telefono duplicado (mismo número que otro cliente)
        if random.random() < 0.06 and len(phones_used) > 1:
            row["telefono"] = random.choice(phones_used[:-1])

        # ~4%: apellido NULL
        if random.random() < 0.04:
            row["apellido"] = ""

        # ~3%: fecha_registro NULL
        if random.random() < 0.03:
            row["fecha_registro"] = ""

        # ~5%: nombre en mayúsculas (inconsistencia de formato)
        if random.random() < 0.05:
            row["nombre"] = row["nombre"].upper()

        rows.append(row)

    # Añadir ~5 duplicados exactos
    for _ in range(5):
        orig = random.choice(rows[:150])
        dup = orig.copy()
        dup["id"] = n + rows.index(orig) + 1
        rows.append(dup)

    # Mezclar para que los duplicados no estén al final
    random.shuffle(rows)
    # Re-asignar IDs secuenciales
    for idx, row in enumerate(rows, start=1):
        row["id"] = idx

    out_path = os.path.join(OUTPUT_DIR, "techstyle_customers_dirty.csv")
    fieldnames = ["id", "nombre", "apellido", "email", "telefono",
                  "region", "fecha_nacimiento", "fecha_registro", "segmento"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] {out_path}  ({len(rows)} filas, con problemas de calidad)")


# ─────────────────────────────────────────────────────────
# LAB SEMANA 4 — 3 fuentes OLTP con inconsistencias
# ─────────────────────────────────────────────────────────
def generate_oltp_files():
    """
    Genera 3 archivos que simulan fuentes OLTP con:
    - Nombres de columnas distintos
    - Formatos de fecha distintos
    - Unidades y monedas sin estandarizar
    """
    start = datetime(2023, 1, 1)
    end   = datetime(2023, 6, 30)  # Solo primer semestre

    # ── oltp_productos.csv ─────────────────────────────────────────────
    prod_rows = []
    for pid, nombre, cat, costo, precio in PRODUCTS:
        stock_actual = random.randint(5, 200)
        prod_rows.append({
            "Cod_Producto":  pid,
            "Descripcion":   nombre,
            "Linea":         cat,          # ← "Linea" en vez de "categoria"
            "Costo_CLP":     costo,
            "PrecioVenta":   precio,       # ← sin "_CLP"
            "Stock_Actual":  stock_actual,
            "Activo":        "SI",
        })
    path = os.path.join(OUTPUT_DIR, "oltp_productos.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(prod_rows[0].keys()))
        writer.writeheader()
        writer.writerows(prod_rows)
    print(f"[OK] {path}  ({len(prod_rows)} productos)")

    # ── oltp_clientes.csv ──────────────────────────────────────────────
    cli_rows = []
    for cid in range(1, 201):
        nombre   = random.choice(NOMBRES)
        apellido = random.choice(APELLIDOS)
        region   = random.choices(REGIONS, weights=REGION_W)[0]
        fecha_reg = random_date(datetime(2020, 1, 1), end)
        cli_rows.append({
            "CustomerID":     cid,
            "NombreCompleto": f"{nombre} {apellido}",  # ← nombre y apellido unidos
            "Correo":         f"{nombre.lower()}.{apellido.lower()}{cid}@gmail.com",
            "Ciudad":         region,                  # ← "Ciudad" en vez de "region"
            # Fecha en formato DD/MM/YYYY (distinto a ventas)
            "FechaRegistro":  fecha_reg.strftime("%d/%m/%Y"),
            "TipoCliente":    random.choice(["Premium", "Estándar", "Básico"]),
        })
    path = os.path.join(OUTPUT_DIR, "oltp_clientes.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(cli_rows[0].keys()))
        writer.writeheader()
        writer.writerows(cli_rows)
    print(f"[OK] {path}  ({len(cli_rows)} clientes)")

    # ── oltp_ventas.csv ────────────────────────────────────────────────
    venta_rows = []
    vid = 5001
    for _ in range(500):
        fecha = random_date(start, end)
        cli_id = random.randint(1, 200)
        prod   = random.choice(PRODUCTS)
        pid, nombre, cat, costo, precio = prod
        cantidad = random.choices([1, 2, 3], weights=[0.70, 0.22, 0.08])[0]
        desc_pct = random.choices([0, 5, 10, 15], weights=[0.55, 0.20, 0.15, 0.10])[0]
        precio_final = round(precio * (1 - desc_pct / 100))

        venta_rows.append({
            "ID_Venta":       vid,
            # Fecha en formato YYYY/MM/DD (distinto a clientes)
            "Fecha_Venta":    fecha.strftime("%Y/%m/%d"),
            "ID_Cliente":     cli_id,
            "Cod_Prod":       pid,          # ← "Cod_Prod" en vez de "Cod_Producto"
            "Cant":           cantidad,     # ← abreviado
            "Precio_Unit":    precio_final,
            "Desc_Pct":       desc_pct,
            "Total_Venta":    precio_final * cantidad,
        })
        vid += 1

    path = os.path.join(OUTPUT_DIR, "oltp_ventas.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(venta_rows[0].keys()))
        writer.writeheader()
        writer.writerows(venta_rows)
    print(f"[OK] {path}  ({len(venta_rows)} ventas)")


# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generando datos sintéticos TechStyle...")
    generate_orders(n_customers=200, n_orders=700)
    generate_dirty_customers(n=200)
    generate_oltp_files()
    print("\n¡Listo! Archivos en:", OUTPUT_DIR)
