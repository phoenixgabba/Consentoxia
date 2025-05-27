import qrcode

# URL del formulario
url = "https://consentoxia.onrender.com"

# Generar el código QR
qr = qrcode.make(url)

# Guardar como imagen
qr.save("formulario_qr.png")

print("✅ Código QR generado y guardado como 'formulario_qr.png'")
