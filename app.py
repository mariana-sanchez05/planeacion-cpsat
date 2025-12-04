from flask import Flask, render_template, request
from scheduler import SchedulerCPsat

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/planificacion")
def planificacion():
    # Datos de ejemplo
    asesores = ["Ana", "Luis", "Carlos"]
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

    # Obtener parámetro del botón (opcional)
    usar_restriccion = request.args.get("restriccion", "no") == "si"

    scheduler = SchedulerCPsat(
        asesores=asesores,
        dias_laborales=dias,
        permitir_restriccion_apertura=usar_restriccion
    )

    df = scheduler.planificar_semana()

    return render_template("resultado.html", tables=[df.to_html(index=False)])


if __name__ == "__main__":
    app.run(debug=True)

