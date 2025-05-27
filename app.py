import os
import base64
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
from functools import wraps
from waitress import serve

app = Flask(__name__)
app.secret_key = 'clave_super_segura_que_debes_cambiar'

UPLOAD_FOLDER = 'firmas'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DOCS_FOLDER = 'consentimientos_docs'
if not os.path.exists(DOCS_FOLDER):
    os.makedirs(DOCS_FOLDER)

USUARIO = 'La Nuit'
CONTRASENA = '1551'

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

    # Guardar datos en archivo JSON
    try:
        consentimiento_id = str(uuid.uuid4())
        data = {
            'id': consentimiento_id,
            'Nombre': full_name,
            'DNI': dni,
            'Edad': age,
            'Fecha Nacimiento': dob,
            'Dirección': address,
            'Localidad': city,
            'Teléfono': phone,
            'Email': email,
            'Problemas Cardíacos': cardiac_issues,
            'Epilepsia': epilepsy,
            'Hepatitis': hepatitis,
            'Sífilis': syphilis,
            'VIH': hiv,
            'Consumo Drogas': drug_use,
            'Consumo Alcohol': alcohol_use,
            'Tatuador': tattoo_artist,
            'Detalles Tatuaje': tattoo_details,
            'Tinta/Acessorios': tattoo_ink,
            'Rep Legal Nombre': legal_guardian,
            'Rep Legal DNI': legal_dni,
            'Rep Legal Fecha Nac': legal_dob,
            'Rep Legal Dirección': legal_address,
            'Rep Legal Localidad': legal_city,
            'Firma Archivo': filename,
            'Fecha Consentimiento': date
        }
        with open(os.path.join(DOCS_FOLDER, f"{consentimiento_id}.json"), 'w', encoding='utf-8') as fjson:
            json.dump(data, fjson, ensure_ascii=False, indent=4)
    except Exception as e:
        return f"Error al guardar en JSON: {e}"

    return "Formulario enviado con éxito"

@app.route('/consentimientos')
@login_required
def ver_consentimientos():
    datos = []
    if os.path.exists(DOCS_FOLDER):
        for filename in os.listdir(DOCS_FOLDER):
            if filename.endswith('.json'):
                ruta = os.path.join(DOCS_FOLDER, filename)
                with open(ruta, encoding='utf-8') as fjson:
                    try:
                        data = json.load(fjson)
                        datos.append(data)
                    except:
                        pass
    return render_template('consentimientos.html', consentimientos=datos)

@app.route('/consentimiento/<consentimiento_id>')
@login_required
def detalle_consentimiento(consentimiento_id):
    path_json = os.path.join(DOCS_FOLDER, f"{consentimiento_id}.json")
    if not os.path.exists(path_json):
        flash("No se encontró el consentimiento solicitado.")
        return redirect(url_for('ver_consentimientos'))
    try:
        with open(path_json, encoding='utf-8') as fjson:
            consentimiento = json.load(fjson)
    except Exception as e:
        flash(f"Error al cargar el consentimiento: {e}")
        return redirect(url_for('ver_consentimientos'))
    return render_template('consentimiento_detalle.html', consentimiento=consentimiento)

@app.route('/firmas/<filename>')
@login_required
def serve_firma(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/borrar_consentimiento', methods=['POST'])
@login_required
def borrar_consentimiento():
    dni = request.form.get('dni')  # Recibimos el dni del formulario

    if not dni:
        flash("No se recibió DNI para borrar el consentimiento.")
        return redirect(url_for('ver_consentimientos'))

    # Buscar el archivo JSON que tenga el DNI que queremos borrar
    consentimiento_a_borrar = None
    firma_a_borrar = None
    for filename in os.listdir(DOCS_FOLDER):
        if filename.endswith('.json'):
            ruta = os.path.join(DOCS_FOLDER, filename)
            try:
                with open(ruta, encoding='utf-8') as fjson:
                    data = json.load(fjson)
                    if data.get('DNI') == dni:
                        consentimiento_a_borrar = ruta
                        firma_a_borrar = data.get('Firma Archivo')
                        break
            except Exception as e:
                flash(f"Error leyendo archivo {filename}: {e}")
                return redirect(url_for('ver_consentimientos'))

    if consentimiento_a_borrar is None:
        flash("No se encontró consentimiento con ese DNI.")
        return redirect(url_for('ver_consentimientos'))

    # Borrar archivo JSON
    try:
        os.remove(consentimiento_a_borrar)
    except Exception as e:
        flash(f"Error borrando archivo de consentimiento: {e}")
        return redirect(url_for('ver_consentimientos'))

    # Borrar archivo de firma si existe
    if firma_a_borrar:
        ruta_firma = os.path.join(UPLOAD_FOLDER, firma_a_borrar)
        if os.path.exists(ruta_firma):
            try:
                os.remove(ruta_firma)
            except Exception as e:
                flash(f"Error borrando archivo de firma: {e}")
                return redirect(url_for('ver_consentimientos'))

    flash("Consentimiento borrado correctamente.")
    return redirect(url_for('ver_consentimientos'))

@app.route('/politica-de-privacidad')
def politica_privacidad():
    return render_template('politica_privacidad.html')

@app.route('/politica-de-cookies')
def politica_cookies():
    return render_template('politica_cookies.html')

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
