# Planeación de Turnos con CP-SAT + Flask

Proyecto de prueba técnica que asigna turnos (Apertura, Intermedio, Cierre) a 3 asesores usando Google OR-Tools CP-SAT.

## Estructura recomendada

planeacion-cpsat/
├── app.py
├── scheduler.py
├── requirements.txt
├── README.md
├── .gitignore
└── templates/
├── index.html
└── resultados.html

markdown
Copiar código

## Requerimientos

- Python 3.9+
- pip

Instalar dependencias:

```bash
pip install -r requirements.txt
Contenido sugerido en requirements.txt:

nginx
Copiar código
flask
pandas
ortools
python-dateutil
Qué hace la app
Genera asignación de turnos para 3 asesores usando CP-SAT.

Cada asesor obtiene exactamente un turno por día.

El turno asignado a un asesor se mantiene constante durante cada semana.

Excluye domingos (no se planifica).

Permite excluir feriados pasando una lista (internamente).

Opción para que una asesora solo trabaje Apertura.

Opción para rotar turnos entre semanas (no repetir el mismo turno la siguiente semana).

Genera un DataFrame con columnas: Week, Date, Advisor, ShiftId, ShiftName.

Permite descargar la planeación en CSV.

Cómo ejecutar
Crear entorno virtual:

bash
Copiar código
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
Instalar dependencias:

bash
Copiar código
pip install -r requirements.txt
Ejecutar la app:

bash
Copiar código
python app.py
Abrir en el navegador:

cpp
Copiar código
http://127.0.0.1:5000
Pruebas recomendadas
Generar planeación normal (1 semana): presionar Generar.

Activar restricción: selecciona una asesora en "Asesora con turno fijo de Apertura" y genera.

Rotación entre semanas: establece Semanas = 2 o 4 y marca "Activar rotación".

Descargar CSV: una vez generada la tabla usa el botón Descargar CSV.

Notas técnicas / mejoras posibles
Actualmente se usa un solver CP-SAT con variables por (semana, asesor) que toman valores 1..3 (turnos).

Si no hay solución factible (p. ej. restricciones contradictorias) la app muestra un mensaje de error.

Mejora posible: permitir carga de feriados desde UI, soporte para N>3 asesores, pruebas unitarias, y una API REST.

yaml
Copiar código

---

## Cómo probar (pasos exactos)

1. Guarda los archivos anteriores (sobrescribe `app.py`, `templates/index.html`, `templates/resultados.html`, `README.md`).
2. Asegúrate de que `scheduler.py` es la versión mejorada que ya tienes (la que expone `planificar_semanas`).
3. Activa tu entorno virtual y reinstala dependencias si hace falta:

```bash
pip install -r requirements.txt
Ejecuta la app:

bash
Copiar código
python app.py
En el navegador abre: http://127.0.0.1:5000

Prueba las combinaciones:

start_date: deja la fecha por defecto (hoy) o selecciona otra.

weeks: prueba 1, 2, 4.

rotation: activa para probar no repetir turnos entre semanas.

restriction: selecciona Ana para probar la asesora fija en Apertura.

Presiona Generar planeación.

Si todo OK verás la tabla, resumen de parámetros y botón Descargar CSV.
