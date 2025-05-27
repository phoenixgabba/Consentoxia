import os
import base64
import csv
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
from functools import wraps
from waitress import serve

app = Flask(__name__)
app.secret_key = 'clave_super_segura_que_debes_cambiar'

UPLOAD_FOLDER = 'firmas'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

USUARIO = 'La Nuit'
CONTRASENA = '1551'
CSV_FILE = 'consentimientos.csv'

# Decorador para requerir login con sesión
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Por favor, inicia sesión para acceder.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USUARIO and password == CONTRASENA:
            session['logged_in'] = True
            flash('Inicio de sesión exitoso.')
            return redirect(url_for('ver_consentimientos'))
        else:
            flash('Usuario o contraseña incorrectos.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Has cerrado sesión.')
    return redirect(url_for('login'))

@app.route('/submit', methods=['POST'])
def submit_form():
    # Recoger todos los campos enviados desde el formulario
    full_name = request.form.get('full_name')
    dni = request.form.get('dni')
    age = request.form.get('age')
    dob = request.form.get('dob')
    address = request.form.get('address')
    city = request.form.get('city')
    phone = request.form.get('phone')
    email = request.form.get('email')

    cardiac_issues = request.form.get('cardiac_issues')
    epilepsy = request.form.get('epilepsy')
    hepatitis = request.form.get('hepatitis')
    syphilis = request.form.get('syphilis')
    hiv = request.form.get('hiv')
    drug_use = request.form.get('drug_use')
    alcohol_use = request.form.get('alcohol_use')

    tattoo_artist = request.form.get('tattoo_artist')
    tattoo_details = request.form.get('tattoo_details')
    tattoo_ink = request.form.get('tattoo_ink')

    legal_guardian = request.form.get('legal_guardian')
    legal_dni = request.form.get('legal_dni')
    legal_dob = request.form.get('legal_dob')
    legal_address = request.form.get('legal_address')
    legal_city = request.form.get('legal_city')

    signature = request.form.get('signature')  # Firma en base64
    date = request.form.get('date')            # Fecha del consentimiento
    consentimiento = request.form.get('consentimiento')

    if not consentimiento:
        return "Debe aceptar los términos de consentimiento para continuar."

    # Guardar la firma como imagen PNG
    filename = ''
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

    # Guardar datos en CSV
    try:
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow([
                    'Nombre', 'DNI', 'Edad', 'Fecha Nacimiento', 'Dirección', 'Localidad', 'Teléfono', 'Email',
                    'Problemas Cardíacos', 'Epilepsia', 'Hepatitis', 'Sífilis', 'VIH',
                    'Consumo Drogas', 'Consumo Alcohol',
                    'Tatuador', 'Detalles Tatuaje', 'Tinta/Acessorios',
                    'Rep Legal Nombre', 'Rep Legal DNI', 'Rep Legal Fecha Nac', 'Rep Legal Dirección', 'Rep Legal Localidad',
                    'Firma Archivo', 'Fecha Consentimiento'
                ])
            writer.writerow([
                full_name, dni, age, dob, address, city, phone, email,
                cardiac_issues, epilepsy, hepatitis, syphilis, hiv,
                drug_use, alcohol_use,
                tattoo_artist, tattoo_details, tattoo_ink,
                legal_guardian, legal_dni, legal_dob, legal_address, legal_city,
                filename, date
            ])
    except Exception as e:
        return f"Error al guardar en CSV: {e}"

    return "Formulario enviado con éxito"

@app.route('/consentimientos')
@login_required
def ver_consentimientos():
    datos = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            datos = list(reader)
    return render_template('consentimientos.html', consentimientos=datos)

@app.route('/firmas/<filename>')
@login_required
def serve_firma(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# --- NUEVO: Ruta para borrar consentimiento ---
@app.route('/borrar_consentimiento', methods=['POST'])
@login_required
def borrar_consentimiento():
    dni_a_borrar = request.form.get('dni')
    if not dni_a_borrar:
        flash("No se recibió DNI para borrar.")
        return redirect(url_for('ver_consentimientos'))

    if not os.path.exists(CSV_FILE):
        flash("No hay registros para borrar.")
        return redirect(url_for('ver_consentimientos'))

    # Leer todos los consentimientos
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile))
        campos = reader[0].keys() if reader else []

    # Filtrar consentimientos, eliminando el que coincide con el DNI
    nuevos_datos = []
    firma_a_borrar = None
    for fila in reader:
        if fila.get('DNI') == dni_a_borrar:
            firma_a_borrar = fila.get('Firma Archivo')
            continue
        nuevos_datos.append(fila)

    # Guardar el CSV sin el consentimiento borrado
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        if campos:
            writer = csv.DictWriter(csvfile, fieldnames=campos)
            writer.writeheader()
            writer.writerows(nuevos_datos)

    # Borrar la imagen de la firma si existe
    if firma_a_borrar:
        ruta_firma = os.path.join(UPLOAD_FOLDER, firma_a_borrar)
        if os.path.exists(ruta_firma):
            os.remove(ruta_firma)

    flash(f"Consentimiento con DNI {dni_a_borrar} borrado correctamente.")
    return redirect(url_for('ver_consentimientos'))

# --- NUEVA RUTA PARA POLITICA DE PRIVACIDAD ---
@app.route('/politica-de-privacidad')
def politica_privacidad():
    return render_template('politica_privacidad.html')

# --- NUEVA RUTA PARA POLITICA DE COOKIES ---
@app.route('/politica-de-cookies')
def politica_cookies():
    return render_template('politica_cookies.html')


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
