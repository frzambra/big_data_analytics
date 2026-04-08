"""
Generador de datos para Solemne 1 — Big Data y Analytics
Universidad San Sebastián

Genera los siguientes archivos en solemnes/data/:
  - solemne_pedidos_planos.csv   → Pregunta 1 (calidad) y Pregunta 3 (normalización)
  - solemne_oltp_pedidos.csv     → Para que el docente construya solemne_modelo.pbix (P2C)
  - solemne_oltp_clientes.csv    → ídem
  - solemne_oltp_restaurantes.csv → ídem

Ejecutar desde la raíz del repositorio:
    python solemnes/generar_datos_solemne.py
"""

import csv
import os
import random
from datetime import date, timedelta

random.seed(42)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# CATÁLOGOS
# ─────────────────────────────────────────────

RESTAURANTES = [
    ("R003", "Burger Bros",   "Americana"),
    ("R005", "El Ceviche",    "Peruana"),
    ("R007", "Taco Loco",     "Mexicana"),
    ("R008", "Pizza Roma",    "Italiana"),
    ("R012", "Sushi Kioto",   "Japonesa"),
    ("R017", "Don Sushi",     "Japonesa"),
]

# (producto_id, nombre, precio_unitario, restaurante_id)
PRODUCTOS = [
    ("PRD001", "Salmón Roll",       9250,  "R012"),
    ("PRD002", "Temaki Mixto",      11000, "R012"),
    ("PRD003", "Ramen Tonkotsu",    9500,  "R012"),
    ("PRD004", "Dragon Roll",       9000,  "R017"),
    ("PRD005", "Pizza Margherita",  8900,  "R008"),
    ("PRD006", "Pizza Napolitana",  12900, "R008"),
    ("PRD007", "Pasta Carbonara",   7600,  "R008"),
    ("PRD008", "Burger Clásica",    9500,  "R003"),
    ("PRD009", "Burger BBQ",        8700,  "R003"),
    ("PRD010", "Papas Fritas",      2500,  "R003"),
    ("PRD011", "Ceviche Clásico",   9500,  "R005"),
    ("PRD012", "Lomo Saltado",      11000, "R005"),
    ("PRD013", "Causa Limeña",      7000,  "R005"),
    ("PRD014", "Tacos al Pastor",   6500,  "R007"),
    ("PRD015", "Burrito Especial",  8000,  "R007"),
    ("PRD016", "Quesadilla",        5500,  "R007"),
]

# Mapa restaurante → lista de productos
PROD_BY_REST = {}
for p in PRODUCTOS:
    PROD_BY_REST.setdefault(p[3], []).append(p)

# (cliente_id, nombre, apellido, email, telefono, comuna)
# C005 y C011 tienen variantes de calidad; C013 email inválido; C019 email vacío
CLIENTES_BASE = [
    ("C001", "Pedro",     "Álvarez",    "pedro.alvarez@gmail.com",       "912345678", "Providencia"),
    ("C002", "Isabel",    "Rojas",      "isabel.rojas@yahoo.com",        "923456789", "Las Condes"),
    ("C003", "Diego",     "Morales",    "diego.morales@gmail.com",       "934567890", "Providencia"),
    ("C004", "Sofía",     "Castro",     "sofia.castro@hotmail.com",      "945678901", "Vitacura"),
    ("C005", "Ana",       "Torres",     "ana.torres@gmail.com",          "956789012", "Ñuñoa"),
    ("C006", "Martín",    "Vega",       "martin.vega@gmail.com",         "967890123", "Maipú"),
    ("C007", "Catalina",  "Muñoz",      "catalina.munoz@gmail.com",      "978901234", "San Miguel"),
    ("C008", "Andrés",    "Pinto",      "andres.pinto@outlook.com",      "989012345", "La Florida"),
    ("C009", "Valentina", "Silva",      "v.silva@empresa.cl",            "990123456", "Peñalolén"),
    ("C010", "Rodrigo",   "Herrera",    "rodrigo.herrera@gmail.com",     "901234567", "Macul"),
    ("C011", "Carlos",    "Mendez",     "carlos.m@gmail.com",            "912345679", "Ñuñoa"),
    ("C012", "Francisca", "Lagos",      "francisca.lagos@gmail.com",     "923456780", "Recoleta"),
    ("C013", "Tomás",     "Espinoza",   "tomas.esp@hotmail",             "934567891", "Cerrillos"),   # email inválido
    ("C014", "Javiera",   "Contreras",  "javiera.c@gmail.com",           "945678902", "Lo Barnechea"),
    ("C015", "Nicolás",   "Farías",     "nicolas.farias@gmail.com",      "956789013", "Pudahuel"),
    ("C019", "María",     "López",      "",                              "967890124", "Las Condes"),  # email vacío
]
CLIENTE_MAP = {c[0]: c for c in CLIENTES_BASE}

REPARTIDORES = ["D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08"]
DESCUENTOS   = [0, 0, 0, 0, 10, 10, 20]   # 0 predomina; se elige aleatoriamente

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def total_pedido(precio, cantidad, descuento_pct):
    return int(precio * cantidad * (1 - descuento_pct / 100))

def random_date(start=date(2024, 1, 10), end=date(2024, 3, 14)):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def make_row(pid, fecha_str, cid, nombre_completo, email, telefono, comuna,
             rid, rest_nombre, categoria, repartidor, tiempo,
             prd_id, prd_nombre, precio, cantidad, descuento):
    total = total_pedido(precio, cantidad, descuento)
    return [pid, fecha_str, cid, nombre_completo, email, telefono, comuna,
            rid, rest_nombre, categoria, repartidor, tiempo,
            prd_id, prd_nombre, precio, cantidad, descuento, total]

def random_row(pid, cid, overrides=None):
    """Genera una fila normal (sin errores de calidad) para un cliente dado."""
    c = CLIENTE_MAP[cid]
    nombre_completo = f"{c[1]} {c[2]}"
    email    = c[3]
    telefono = c[4]
    comuna   = c[5]

    rid, rest_nombre, categoria = random.choice(RESTAURANTES)
    prd = random.choice(PROD_BY_REST[rid])
    prd_id, prd_nombre, precio, _ = prd

    rep      = random.choice(REPARTIDORES)
    tiempo   = random.randint(18, 55)
    cantidad = random.randint(1, 2)
    desc     = random.choice(DESCUENTOS)
    fecha    = random_date().isoformat()

    if overrides:
        local = {
            "fecha": fecha, "nombre_completo": nombre_completo,
            "email": email, "telefono": telefono, "comuna": comuna,
            "rid": rid, "rest_nombre": rest_nombre, "categoria": categoria,
            "rep": rep, "tiempo": tiempo,
            "prd_id": prd_id, "prd_nombre": prd_nombre,
            "precio": precio, "cantidad": cantidad, "desc": desc,
        }
        local.update(overrides)
        fecha         = local["fecha"]
        nombre_completo = local["nombre_completo"]
        email         = local["email"]
        telefono      = local["telefono"]
        comuna        = local["comuna"]
        rid           = local["rid"]
        rest_nombre   = local["rest_nombre"]
        categoria     = local["categoria"]
        rep           = local["rep"]
        tiempo        = local["tiempo"]
        prd_id        = local["prd_id"]
        prd_nombre    = local["prd_nombre"]
        precio        = local["precio"]
        cantidad      = local["cantidad"]
        desc          = local["desc"]

    return make_row(pid, fecha, cid, nombre_completo, email, telefono, comuna,
                    rid, rest_nombre, categoria, rep, tiempo,
                    prd_id, prd_nombre, precio, cantidad, desc)


# ─────────────────────────────────────────────
# 1. solemne_pedidos_planos.csv
# ─────────────────────────────────────────────

HEADER_PLANOS = [
    "id_pedido", "fecha_pedido", "cliente_id", "cliente_nombre",
    "cliente_email", "cliente_telefono", "cliente_comuna",
    "restaurante_id", "restaurante_nombre", "categoria_cocina",
    "repartidor_id", "tiempo_entrega_min",
    "producto_id", "producto_nombre",
    "precio_unitario", "cantidad", "descuento_pct", "total_pedido",
]

# ── Filas del extracto (deben coincidir EXACTAMENTE con el enunciado) ──────
FILAS_EXTRACTO = [
    # P001: fecha ISO, email válido, Ñuñoa ✓
    make_row("P001", "2024-03-15", "C005", "Ana Torres",
             "ana.torres@gmail.com",  "956789012", "Ñuñoa",
             "R012", "Sushi Kioto", "Japonesa", "D03", 35,
             "PRD001", "Salmón Roll", 9250, 2, 0),

    # P002: fecha DD/MM/YYYY + email sin dominio (.com faltante) ← problemas 1 y 2
    make_row("P002", "15/03/2024", "C005", "Ana Torres",
             "ana.torres@hotmail",   "956789012", "Ñuñoa",
             "R008", "Pizza Roma", "Italiana", "D05", 28,
             "PRD006", "Pizza Napolitana", 12900, 1, 0),

    # P003: tiempo_entrega_min negativo + comuna en MAYÚSCULAS + nombre en minúsculas ← problemas 3 y 4 y 5
    make_row("P003", "2024-03-16", "C011", "carlos mendez",
             "carlos.m@gmail.com",   "912345679", "ÑUÑOA",
             "R012", "Sushi Kioto", "Japonesa", "D03", -12,
             "PRD002", "Temaki Mixto", 11000, 2, 0),

    # P004: email vacío (C019) ← problema 6
    make_row("P004", "2024-03-16", "C019", "María López",
             "",                     "967890124", "Las Condes",
             "R003", "Burger Bros", "Americana", "D07", 42,
             "PRD008", "Burger Clásica", 9500, 1, 0),

    # P005: comuna "Nuñoa" (variante sin tilde) + categoria en minúsculas ← problema 4 y 7
    make_row("P005", "2024-03-17", "C005", "Ana Torres",
             "ana.torres@gmail.com", "956789012", "Nuñoa",
             "R008", "Pizza Roma", "italiana", "D05", 31,
             "PRD007", "Pasta Carbonara", 7600, 2, 0),

    # P006: datos correctos de C011 (mismo cliente que P003, diferente capitalización = anomalía de actualización)
    make_row("P006", "2024-03-17", "C011", "Carlos Mendez",
             "carlos.m@gmail.com",  "912345679", "Ñuñoa",
             "R003", "Burger Bros", "Americana", "D07", 55,
             "PRD009", "Burger BBQ", 8700, 1, 0),
]

# ── Filas adicionales (datos limpios + repetición de anomalías en C005, C011, C013, C019) ──

filas_normales = []
pid_counter = 7   # empezamos en P007

def next_pid():
    global pid_counter
    p = f"P{pid_counter:03d}"
    pid_counter += 1
    return p

# Clientes "limpios": C001–C004, C006–C010, C012, C014, C015
clientes_limpios = ["C001","C002","C003","C004","C006","C007","C008","C009","C010","C012","C014","C015"]

for _ in range(40):
    cid = random.choice(clientes_limpios)
    filas_normales.append(random_row(next_pid(), cid))

# C005: aparece con variantes de comuna (anomalía de actualización: mismo ID, datos distintos)
variantes_c005 = [
    {"comuna": "Ñuñoa",  "email": "ana.torres@gmail.com"},   # correcto
    {"comuna": "Ñuñoa",  "email": "ana.torres@gmail.com"},   # correcto
    {"comuna": "ÑUÑOA",  "email": "ana.torres@gmail.com"},   # inconsistencia
    {"comuna": "Nuñoa",  "email": "ana.torres@gmail.com"},   # inconsistencia
    {"comuna": "Ñuñoa",  "email": "ana.torres@hotmail.com"}, # email distinto (anomalía actualización)
    {"comuna": "Ñuñoa",  "email": "ana.torres@gmail.com"},   # correcto
]
for v in variantes_c005:
    filas_normales.append(random_row(next_pid(), "C005", overrides=v))

# C011: variantes de nombre (anomalía de actualización en el nombre)
variantes_c011 = [
    {"nombre_completo": "Carlos Mendez",  "comuna": "Ñuñoa"},
    {"nombre_completo": "carlos mendez",  "comuna": "Nuñoa"},
    {"nombre_completo": "Carlos Mendez",  "comuna": "Ñuñoa"},
    {"nombre_completo": "CARLOS MENDEZ",  "comuna": "Ñuñoa"},
    {"nombre_completo": "Carlos Mendez",  "comuna": "Ñuñoa"},
]
for v in variantes_c011:
    filas_normales.append(random_row(next_pid(), "C011", overrides=v))

# C013: email inválido en TODOS sus pedidos (consistente)
for _ in range(6):
    filas_normales.append(random_row(next_pid(), "C013",
                                     overrides={"email": "tomas.esp@hotmail"}))

# C019: email siempre vacío
for _ in range(5):
    filas_normales.append(random_row(next_pid(), "C019",
                                     overrides={"email": ""}))

# Las filas del extracto conservan P001–P006.
# El resto se ordena cronológicamente y se numera a partir de P007.
def fecha_sort_key(row):
    f = row[1]
    if "/" in f:                        # DD/MM/YYYY → convertir para ordenar
        d, m, y = f.split("/")
        return f"{y}-{m}-{d}"
    return f

filas_normales.sort(key=fecha_sort_key)
for i, row in enumerate(filas_normales, start=7):
    row[0] = f"P{i:03d}"

todas = FILAS_EXTRACTO + filas_normales

# ── Escribir CSV ──────────────────────────────
path_planos = os.path.join(OUTPUT_DIR, "solemne_pedidos_planos.csv")
with open(path_planos, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(HEADER_PLANOS)
    w.writerows(todas)

print(f"✓  solemne_pedidos_planos.csv  ({len(todas)} filas)")


# ─────────────────────────────────────────────
# 2. solemne_oltp_pedidos.csv  (para construir el .pbix)
#    Columnas con nombres sucios + fechas DD/MM/YYYY + algunos Total_Venta = 0
# ─────────────────────────────────────────────

HEADER_OLTP_PED = [
    "ID_Pedido", "Fecha_Venta", "ID_Cliente", "RestauranteID",
    "Cod_Prod", "Cant", "Precio_Unit", "Desc_Pct", "Total_Venta", "Tiempo_Entrega",
]

oltp_ped_rows = []
for i, row in enumerate(todas[:50], start=1):   # usamos los primeros 50 pedidos como fuente
    _, fecha_iso, cid, _, _, _, _, rid, _, _, _, tiempo_entrega, prd_id, _, precio, cantidad, desc, total = row
    # Convertir fecha a DD/MM/YYYY
    if "-" in fecha_iso and len(fecha_iso) == 10:
        y, m, d = fecha_iso.split("-")
        fecha_oltp = f"{d}/{m}/{y}"
    else:
        fecha_oltp = fecha_iso   # ya está en DD/MM/YYYY

    # Errores fijos en filas específicas (deterministas, sin aleatoriedad):
    # filas 5 y 10 → Total_Venta = 0 (importe sin registrar)
    # fila 15      → Total_Venta negativo (devolución mal registrada)
    if i in (5, 10):
        total_oltp = 0
    elif i == 15:
        total_oltp = -total
    else:
        total_oltp = total

    oltp_ped_rows.append([
        f"PED{i:03d}", fecha_oltp, cid, rid,
        prd_id, cantidad, precio, desc, total_oltp, tiempo_entrega,
    ])

path_oltp_ped = os.path.join(OUTPUT_DIR, "solemne_oltp_pedidos.csv")
with open(path_oltp_ped, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(HEADER_OLTP_PED)
    w.writerows(oltp_ped_rows)

print(f"✓  solemne_oltp_pedidos.csv    ({len(oltp_ped_rows)} filas)")


# ─────────────────────────────────────────────
# 3. solemne_oltp_clientes.csv  (para construir el .pbix)
#    CustomerID (≠ ID_Cliente), Ciudad inconsistente, algunos emails nulos
# ─────────────────────────────────────────────

HEADER_OLTP_CLI = [
    "CustomerID", "NombreCompleto", "Correo", "Ciudad", "FechaRegistro", "TipoCliente",
]

# Variantes sucias de ciudad
CIUDAD_SUCIA = {
    "Providencia":  ["Providencia", "PROVIDENCIA", "providencia"],
    "Las Condes":   ["Las Condes",  "LAS CONDES",  "Las condes"],
    "Vitacura":     ["Vitacura",    "Vitacura",    "VITACURA"],
    "Ñuñoa":        ["Ñuñoa",       "ÑUÑOA",       "Nuñoa"],
    "Maipú":        ["Maipú",       "MAIPU",       "Maipú"],
    "San Miguel":   ["San Miguel",  "San miguel",  "SAN MIGUEL"],
    "La Florida":   ["La Florida",  "LA FLORIDA",  "La florida"],
    "Peñalolén":    ["Peñalolén",   "PEÑALOLEN",   "Peñalolen"],
    "Macul":        ["Macul",       "MACUL",       "macul"],
    "Recoleta":     ["Recoleta",    "RECOLETA",    "recoleta"],
    "Cerrillos":    ["Cerrillos",   "CERRILLOS",   "cerrillos"],
    "Lo Barnechea": ["Lo Barnechea","Lo barnechea","LO BARNECHEA"],
    "Pudahuel":     ["Pudahuel",    "PUDAHUEL",    "pudahuel"],
}

SEGMENTOS    = ["Premium", "Estándar", "Básico"]
FECHA_BASE   = date(2022, 1, 1)

oltp_cli_rows = []
for c in CLIENTES_BASE:
    cid, nombre, apellido, email, telefono, comuna = c
    nombre_completo = f"{nombre} {apellido}"
    ciudad_variante = random.choice(CIUDAD_SUCIA.get(comuna, [comuna]))
    # Correo vacío en clientes específicos (determinista):
    # C019 siempre vacío; C010 y C015 también — total: 3 clientes sin Correo
    correo = "" if cid in ("C010", "C015", "C019") else email
    fecha_reg = (FECHA_BASE + timedelta(days=random.randint(0, 600))).strftime("%d/%m/%Y")
    segmento  = random.choice(SEGMENTOS)
    oltp_cli_rows.append([cid, nombre_completo, correo, ciudad_variante, fecha_reg, segmento])

path_oltp_cli = os.path.join(OUTPUT_DIR, "solemne_oltp_clientes.csv")
with open(path_oltp_cli, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(HEADER_OLTP_CLI)
    w.writerows(oltp_cli_rows)

print(f"✓  solemne_oltp_clientes.csv   ({len(oltp_cli_rows)} filas)")


# ─────────────────────────────────────────────
# 4. solemne_oltp_restaurantes.csv  (para construir el .pbix)
#    Linea con capitalización inconsistente
# ─────────────────────────────────────────────

HEADER_OLTP_REST = ["RestauranteID", "Nombre_Rest", "Linea", "Activo"]

LINEA_SUCIA = {
    "Americana": ["Americana", "AMERICANA", "americana"],
    "Peruana":   ["Peruana",   "PERUANA",   "peruana"],
    "Mexicana":  ["Mexicana",  "MEXICANA",  "mexicana"],
    "Italiana":  ["Italiana",  "ITALIANA",  "italiana"],
    "Japonesa":  ["Japonesa",  "JAPONESA",  "japonesa"],
}

oltp_rest_rows = []
for rid, nombre, categoria in RESTAURANTES:
    linea_variante = random.choice(LINEA_SUCIA.get(categoria, [categoria]))
    oltp_rest_rows.append([rid, nombre, linea_variante, "TRUE"])

path_oltp_rest = os.path.join(OUTPUT_DIR, "solemne_oltp_restaurantes.csv")
with open(path_oltp_rest, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(HEADER_OLTP_REST)
    w.writerows(oltp_rest_rows)

print(f"✓  solemne_oltp_restaurantes.csv ({len(oltp_rest_rows)} filas)")

print("\nListo. Archivos generados en solemnes/data/")
print("""
─────────────────────────────────────────────────────────────────────
Para construir solemne_modelo.pbix (P2C):
  1. Abrir Power BI Desktop
  2. Cargar los tres archivos solemne_oltp_*.csv
  3. En Power Query: renombrar columnas, corregir fechas, filtrar Total_Venta > 0,
     estandarizar Ciudad y Linea, separar NombreCompleto en nombre/apellido
  4. Crear relaciones:
       oltp_pedidos[ID_Cliente]    → oltp_clientes[CustomerID]  (N:1)
       oltp_pedidos[RestauranteID] → oltp_restaurantes[RestauranteID] (N:1)
  5. Guardar como solemne_modelo.pbix y distribuir a los estudiantes
─────────────────────────────────────────────────────────────────────
""")
