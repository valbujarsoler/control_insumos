from database import get_connection

# ======================
# MÉDICOS
# ======================
def agregar_medico(nombre):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO medicos (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()

def obtener_medicos():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM medicos")
    data = c.fetchall()
    conn.close()
    return data

# ======================
# ANESTESIÓLOGOS
# ======================
def agregar_anestesiologo(nombre):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO anestesiologos (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()

def obtener_anestesiologos():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM anestesiologos")
    data = c.fetchall()
    conn.close()
    return data

# ======================
# ENFERMEROS
# ======================
def agregar_enfermero(nombre):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO enfermeros (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()

def obtener_enfermeros():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM enfermeros")
    data = c.fetchall()
    conn.close()
    return data

# ======================
# PACIENTES
# ======================
def agregar_paciente(nombre, procedencia, medico_id, diagnostico, anestesiologo_id, enfermero_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO pacientes (nombre, procedencia, medico_id, diagnostico, anestesiologo_id, enfermero_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, procedencia, medico_id, diagnostico, anestesiologo_id, enfermero_id))
    conn.commit()
    conn.close()

def obtener_pacientes():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT p.id, p.nombre, p.procedencia, m.nombre as medico, p.diagnostico, a.nombre as anestesiologo, e.nombre as enfermero
        FROM pacientes p
        LEFT JOIN medicos m ON p.medico_id = m.id
        LEFT JOIN anestesiologos a ON p.anestesiologo_id = a.id
        LEFT JOIN enfermeros e ON p.enfermero_id = e.id
    """)
    data = c.fetchall()
    conn.close()
    return data

# ======================
# CATALOGO DE INSUMOS
# ======================
def agregar_insumo(nombre):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO insumos_lista (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()

def obtener_insumos():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM insumos_lista")
    data = c.fetchall()
    conn.close()
    return data

# ======================
# APLICACIONES
# ======================
def agregar_aplicacion(paciente_id, numero_aplicacion, fecha):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO aplicaciones (paciente_id, numero_aplicacion, fecha) VALUES (?, ?, ?)",
              (paciente_id, numero_aplicacion, fecha))
    app_id = c.lastrowid
    conn.commit()
    conn.close()
    return app_id

def obtener_aplicaciones(paciente_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM aplicaciones WHERE paciente_id = ?", (paciente_id,))
    data = c.fetchall()
    conn.close()
    return data

# ======================
# INSUMOS POR APLICACIÓN
# ======================
def agregar_insumo_a_aplicacion(aplicacion_id, insumo_id, cantidad):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO insumos (aplicacion_id, insumo_id, cantidad) VALUES (?, ?, ?)",
              (aplicacion_id, insumo_id, cantidad))
    conn.commit()
    conn.close()

def obtener_insumos_de_aplicacion(aplicacion_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT il.nombre, i.cantidad
        FROM insumos i
        JOIN insumos_lista il ON i.insumo_id = il.id
        WHERE i.aplicacion_id = ?
    """, (aplicacion_id,))
    data = c.fetchall()
    conn.close()
    return data

# ======================
# LISTA SIMPLE DE INSUMOS PARA FORMULARIOS
# ======================
def obtener_insumos_lista():
    """
    Devuelve una lista de nombres de insumos para usar en formularios.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT nombre FROM insumos_lista ORDER BY nombre")
    data = [row[0] for row in c.fetchall()]
    conn.close()
    return data
