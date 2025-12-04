# Planeación de Turnos con CP-SAT + Flask
Prueba técnica desarrollada en Python usando:

- OR-Tools CP-SAT
- Flask
- Pandas

## Estructura
planeacion-cpsat/
│── app.py
│── scheduler.py
│── run_example.py
│── requirements.txt
│── README.md
│── .gitignore
│── static/
│── templates/

shell
Copiar código

## Ejecución local

### 1) Crear entorno
python -m venv .venv
..venv\Scripts\activate # Windows
source .venv/bin/activate # Linux/Mac

shell
Copiar código

### 2) Instalar dependencias
pip install -r requirements.txt

shell
Copiar código

### 3) Probar el modelo sin Flask
python run_example.py

shell
Copiar código

### 4) Ejecutar Flask
python app.py

yaml
Copiar código

Abrir en navegador:
http://127.0.0.1:5000

markdown
Copiar código

## Funcionalidades
- Asignación automática de turnos con CP-SAT
- Restricción opcional: asesora fija en turno de apertura
- Tabla HTML con los resultados
