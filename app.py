import os
import base64
from flask import Flask, render_template, request
from waitress import serve

app = Flask(__name__)

# Carpeta para guardar las firmas
UPLOAD_FOLDER = 'firmas'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    full_name = request.form.get('full_name')
    dob = request.form.get('dob')
    contact_info = request.form.get('contact_info')
    health_conditions = request.form.get('health_conditions')
    signature = request.form.get('signature')  # Firma en base64
    date = request.form.get('date')            # Fecha del consentimiento
    consentimiento = request.form.get('consentimiento')

    if not consentimiento:
        return "Debe aceptar los términos de consentimiento para continuar."

    # Guardar la firma como imagen PNG
    if signature and signature != 'data:,':
        try:
            header, encoded = signature.split(',', 1)
            data = base64.b64decode(encoded)
            filename = f"{full_name.replace(' ', '_')}_firma.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, 'wb') as f:
                f.write(data)
        except Exception as e:
            return f"Error al guardar la firma: {e}"

    # Mostrar datos en consola (puedes cambiar por lógica propia)
    print(f"Nombre: {full_name}")
    print(f"Fecha de Nacimiento: {dob}")
    print(f"Contacto: {contact_info}")
    print(f"Condiciones de Salud: {health_conditions}")
    print(f"Firma guardada en: {filepath if signature else 'No proporcionada'}")
    print(f"Fecha de Consentimiento: {date}")

    if consentimiento == 'true':
        print(f"Consentimiento para recibir publicidad: {contact_info}")

    return "Formulario enviado con éxito"

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
