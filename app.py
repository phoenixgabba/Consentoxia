from flask import Flask, render_template, request
from waitress import serve
from app import app  # Asegúrate de que 'app' es tu instancia de Flask

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    full_name = request.form.get('full_name')
    dob = request.form.get('dob')
    contact_info = request.form.get('contact_info')
    health_conditions = request.form.get('health_conditions')
    signature = request.form.get('signature')
    date = request.form.get('date')
    consentimiento = request.form.get('consentimiento')

    if not consentimiento:
        return "Debe aceptar los términos de consentimiento para continuar."

    # Aquí podrías guardar los datos o enviarlos por correo
    # En este caso, solo los mostramos en la consola
    print(f"Nombre: {full_name}")
    print(f"Fecha de Nacimiento: {dob}")
    print(f"Contacto: {contact_info}")
    print(f"Condiciones de Salud: {health_conditions}")
    print(f"Firma: {signature}")
    print(f"Fecha de Consentimiento: {date}")

    # Aquí puedes agregar la lógica para enviar publicidad si lo deseas
    # Ejemplo simple de impresión del consentimiento:
    if consentimiento == 'true':
        print(f"Consentimiento para recibir publicidad: {contact_info}")
    
    return "Formulario enviado con éxito"

if __name__ == '__main__':
    app.run(debug=True)
