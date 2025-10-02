from flask import Flask, render_template, request, redirect, url_for
from database import create_tables, poblar_insumos
import sqlite3

from models import (
    agregar_medico, obtener_medicos,
    agregar_anestesiologo, obtener_anestesiologos,
    agregar_enfermero, obtener_enfermeros,
    agregar_paciente, obtener_pacientes,
    agregar_insumo, obtener_insumos,
    agregar_aplicacion, obtener_aplicaciones,
    agregar_insumo_a_aplicacion, obtener_insumos_de_aplicacion
)

app = Flask(__name__)

# Crear tablas e insertar catálogo inicial (solo 1 vez al arrancar)
create_tables()
poblar_insumos()

# RUTAS
@app.route("/")
def home():
    return render_template("home.html")

# Médicos
@app.route("/medicos", methods=["GET", "POST"])
def medicos():
    if request.method == "POST":
        agregar_medico(request.form["nombre"])
        return redirect(url_for("medicos"))
    lista = obtener_medicos()
    return render_template("medicos.html", medicos=lista)

# Anestesiólogos
@app.route("/anestesiologos", methods=["GET", "POST"])
def anestesiologos():
    if request.method == "POST":
        agregar_anestesiologo(request.form["nombre"])
        return redirect(url_for("anestesiologos"))
    lista = obtener_anestesiologos()
    return render_template("anestesiologos.html", anestesiologos=lista)

# Enfermeros
@app.route("/enfermeros", methods=["GET", "POST"])
def enfermeros():
    if request.method == "POST":
        agregar_enfermero(request.form["nombre"])
        return redirect(url_for("enfermeros"))
    lista = obtener_enfermeros()
    return render_template("enfermeros.html", enfermeros=lista)

# Pacientes
@app.route("/pacientes", methods=["GET", "POST"])
def pacientes():
    if request.method == "POST":
        # convertir IDs a int por seguridad
        medico_id = int(request.form["medico_id"])
        anestesiologo_id = int(request.form["anestesiologo_id"])
        enfermero_id = int(request.form["enfermero_id"])

        agregar_paciente(
            request.form["nombre"],
            request.form["procedencia"],
            medico_id,
            request.form["diagnostico"],
            anestesiologo_id,
            enfermero_id
        )
        return redirect(url_for("pacientes"))

    lista = obtener_pacientes()
    medicos = obtener_medicos()
    anestesiologos = obtener_anestesiologos()
    enfermeros = obtener_enfermeros()
    return render_template("pacientes.html", pacientes=lista,
                           medicos=medicos, anestesiologos=anestesiologos, enfermeros=enfermeros)
# ======================
# REPORTE DE PACIENTES
# ======================
@app.route("/reporte_pacientes")
def reporte_pacientes():
    lista = obtener_pacientes()
    return render_template("reporte_pacientes.html", pacientes=lista)

# Catálogo insumos (ver / agregar insumos al catálogo)
@app.route("/insumos", methods=["GET", "POST"])
def insumos():
    if request.method == "POST":
        agregar_insumo(request.form["nombre"])
        return redirect(url_for("insumos"))
    lista = obtener_insumos()  # devuelve (id, nombre)
    return render_template("insumos.html", insumos=lista)

# Registrar insumos (form general que pide paciente + fecha + cantidades)
@app.route("/aplicacion", methods=["GET", "POST"])
def aplicacion():
    pacientes = obtener_pacientes()    # lista de tuplas
    insumos = obtener_insumos()        # lista de tuplas (id, nombre)

    if request.method == "POST":
        paciente_id = int(request.form["paciente_id"])
        fecha = request.form["fecha"]

        aplicaciones_previas = obtener_aplicaciones(paciente_id)
        numero_aplicacion = len(aplicaciones_previas) + 1
        aplicacion_id = agregar_aplicacion(paciente_id, numero_aplicacion, fecha)

        # Guardar insumos: input names son insumo_{id}
        for insumo in insumos:
            insumo_id = insumo[0]
            cantidad = int(request.form.get(f"insumo_{insumo_id}", 0) or 0)
            if cantidad > 0:
                agregar_insumo_a_aplicacion(aplicacion_id, insumo_id, cantidad)

        # redirigimos al historial del paciente (ya existe)
        return redirect(url_for("historial", paciente_id=paciente_id))

    return render_template("registrar_insumos.html", pacientes=pacientes, insumos=insumos)

# Historial por paciente (muestra aplicaciones y sus insumos)
@app.route("/historial/<int:paciente_id>")
def historial(paciente_id):
    paciente = None
    for p in obtener_pacientes():
        if p[0] == paciente_id:
            paciente = p
            break
    if not paciente:
        return "Paciente no encontrado", 404

    aplicaciones = obtener_aplicaciones(paciente_id)  # lista de tuplas (id,paciente_id,numero,fecha)
    historial = []
    for app_row in aplicaciones:
        insumos = obtener_insumos_de_aplicacion(app_row[0])  # lista de (nombre,cantidad)
        historial.append({"app": app_row, "insumos": insumos})

    return render_template("historial.html", historial=historial, paciente=paciente)
# ================= REPORTE TOTAL DE INSUMOS =================
from flask import Flask, render_template, request, redirect, url_for, Response
import sqlite3
import csv
import io

# ================= REPORTE TOTAL DE INSUMOS =================
@app.route("/reporte_total_insumos", methods=["GET", "POST"])
def reporte_total_insumos():
    conn = sqlite3.connect("data/database.db")
    c = conn.cursor()

    # Filtros
    anio = request.form.get("anio")
    fecha_inicio = request.form.get("fecha_inicio")
    fecha_fin = request.form.get("fecha_fin")

    query = """
        SELECT a.fecha, il.nombre, i.cantidad
        FROM insumos i
        JOIN insumos_lista il ON i.insumo_id = il.id
        JOIN aplicaciones a ON i.aplicacion_id = a.id
        WHERE 1=1
    """
    params = []

    if anio:
        query += " AND strftime('%Y', a.fecha) = ?"
        params.append(anio)
    if fecha_inicio:
        query += " AND date(a.fecha) >= date(?)"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND date(a.fecha) <= date(?)"
        params.append(fecha_fin)

    query += " ORDER BY a.fecha DESC, il.nombre"

    c.execute(query, params)
    data = c.fetchall()
    conn.close()

    return render_template("reporte_total_insumos.html", data=data, anio=anio, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


# ================= EXPORTAR CSV =================
@app.route("/exportar_insumos_csv")
def exportar_insumos_csv():
    conn = sqlite3.connect("data/database.db")
    c = conn.cursor()

    c.execute("""
        SELECT a.fecha, il.nombre, i.cantidad
        FROM insumos i
        JOIN insumos_lista il ON i.insumo_id = il.id
        JOIN aplicaciones a ON i.aplicacion_id = a.id
        ORDER BY a.fecha DESC, il.nombre
    """)
    data = c.fetchall()
    conn.close()

    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fecha", "Insumo", "Cantidad"])
    writer.writerows(data)

    # Respuesta con CSV
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=reporte_insumos.csv"
    return response




if __name__ == "__main__":
    app.run(debug=True)
