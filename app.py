from flask import Flask, render_template, request, url_for, send_file
from scheduler import SchedulerCPsat, SchedulerError
from datetime import date
import io
import pandas as pd

app = Flask(__name__)


@app.route("/")
def index():
    """
    Página principal: formulario para parámetros de planificación:
    - start_date (date)
    - weeks (1-4)
    - rotation (checkbox)
    - restriction (select: ninguno o nombre del asesor)
    """
    # Valores por defecto para la UI
    default_start = date.today().isoformat()
    default_weeks = 1
    advisors = ["Ana", "Luis", "Carlos"]
    return render_template("index.html",
                           start_date=default_start,
                           advisors=advisors,
                           default_weeks=default_weeks)


@app.route("/planificacion")
def planificacion():
    # Leer parámetros desde query string (viene del formulario GET)
    start_date = request.args.get("start_date") or date.today().isoformat()
    weeks = int(request.args.get("weeks") or 1)
    rotation = True if request.args.get("rotation") == "si" else False
    restriction = request.args.get("restriction") or ""  # nombre del asesor o ""

    # Validaciones básicas
    if weeks < 1:
        weeks = 1
    if weeks > 8:
        weeks = 8  # límite razonable

    advisors = ["Ana", "Luis", "Carlos"]

    # Construir scheduler
    scheduler = SchedulerCPsat(
        asesores=advisors,
        permitir_restriccion_apertura=(True if restriction else False)
    )

    try:
        df = scheduler.planificar_semanas(
            start_date=start_date,
            weeks=weeks,
            holidays=[],
            enforce_open_only_for=restriction if restriction else None,
            enforce_open_only_flag=bool(restriction),
            rotation_between_weeks=rotation
        )
    except SchedulerError as e:
        # Mostrar error amigable en HTML con link de vuelta
        return render_template("resultados.html", error=str(e), tabla="", params={
            "start_date": start_date,
            "weeks": weeks,
            "rotation": rotation,
            "restriction": restriction
        })

    # Convertir a HTML
    table_html = df.to_html(index=False, classes="table", justify="left")

    # Preparar URL de descarga con los mismos parámetros
    download_url = url_for('download',
                           start_date=start_date,
                           weeks=weeks,
                           rotation="si" if rotation else "no",
                           restriction=restriction)

    params = {
        "start_date": start_date,
        "weeks": weeks,
        "rotation": rotation,
        "restriction": restriction
    }

    return render_template("resultados.html", tabla=table_html, params=params, download_url=download_url)


@app.route("/download")
def download():
    """
    Genera la planeación con los mismos parámetros y devuelve CSV como descarga.
    Parámetros esperados: start_date, weeks, rotation, restriction
    """
    start_date = request.args.get("start_date") or date.today().isoformat()
    weeks = int(request.args.get("weeks") or 1)
    rotation = True if request.args.get("rotation") == "si" else False
    restriction = request.args.get("restriction") or ""

    advisors = ["Ana", "Luis", "Carlos"]
    scheduler = SchedulerCPsat(
        asesores=advisors,
        permitir_restriccion_apertura=(True if restriction else False)
    )

    try:
        df = scheduler.planificar_semanas(
            start_date=start_date,
            weeks=weeks,
            holidays=[],
            enforce_open_only_for=restriction if restriction else None,
            enforce_open_only_flag=bool(restriction),
            rotation_between_weeks=rotation
        )
    except SchedulerError as e:
        return f"Error al generar CSV: {e}", 400

    # Crear CSV en memoria
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    buf = io.BytesIO(csv_bytes)
    buf.seek(0)

    return send_file(buf,
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name="planeacion.csv")


if __name__ == "__main__":
    app.run(debug=True)


