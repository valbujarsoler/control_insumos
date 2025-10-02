import sqlite3

DB_PATH = "data/database.db"


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Médicos
    c.execute("""
        CREATE TABLE IF NOT EXISTS medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

    # Anestesiólogos
    c.execute("""
        CREATE TABLE IF NOT EXISTS anestesiologos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

    # Enfermeros
    c.execute("""
        CREATE TABLE IF NOT EXISTS enfermeros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

    # Pacientes
    c.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            procedencia TEXT,
            medico_id INTEGER,
            diagnostico TEXT,
            anestesiologo_id INTEGER,
            enfermero_id INTEGER,
            FOREIGN KEY (medico_id) REFERENCES medicos(id),
            FOREIGN KEY (anestesiologo_id) REFERENCES anestesiologos(id),
            FOREIGN KEY (enfermero_id) REFERENCES enfermeros(id)
        )
    """)

    # Aplicaciones
    c.execute("""
        CREATE TABLE IF NOT EXISTS aplicaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            numero_aplicacion INTEGER,
            fecha TEXT,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    # Catálogo de insumos
    c.execute("""
        CREATE TABLE IF NOT EXISTS insumos_lista (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)

    # Insumos usados en cada aplicación
    c.execute("""
        CREATE TABLE IF NOT EXISTS insumos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aplicacion_id INTEGER,
            insumo_id INTEGER,
            cantidad INTEGER,
            FOREIGN KEY (aplicacion_id) REFERENCES aplicaciones(id),
            FOREIGN KEY (insumo_id) REFERENCES insumos_lista(id)
        )
    """)

    conn.commit()
    conn.close()


def poblar_insumos():
    """Inserta insumos por defecto en insumos_lista si no existen"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    insumos = [
        "BATA (PARES)", "BOTA (PARES)", "GORRO", "SONDA FOLEY",
        "BOLSA COLECTORA ORINA", "LIDOCAINA (CC)", "GASA LAVADO",
        "APÓSITOS", "CONTRASTE (ML)", "CLORURO DE SODIO (ML)",
        "JERINGA 10CC", "JERINGA 5CC", "JERINGA 3CC",
        "YODOPOVIDONA (ML)", "ABOCATH", "EQUIPO VENECLICIS",
        "GUANTE QUIRURGICO", "GUANTES DES.", "ESPARADRAPO (CM)",
        "ALGODÓN", "CAMPO ESTERIL", "AGUA OXIGENADA (ML)", "BOLSA ROJA",
        "OXIGENO", "CANULA BINASAL", "JERINGA 20CC",
        "DETERGENTE ENZIMTICO (ML)", "CINTA TESTIGO (CM)",
        "METAMIZOL", "DEXAMETASONA", "TRAMADOL", "DIMENHIDRINATO",
        "METOCLOPRAMIDA", "CLORFENAMINA", "EPINEFRINA", "ÁCIDO TRANEXÁMICO"
    ]

    for insumo in insumos:
        try:
            c.execute("INSERT INTO insumos_lista (nombre) VALUES (?)", (insumo,))
        except sqlite3.IntegrityError:
            pass  # ya existe, lo ignoramos

    conn.commit()
    conn.close()


def get_connection():
    """Devuelve una conexión a la base de datos"""
    return sqlite3.connect(DB_PATH)
