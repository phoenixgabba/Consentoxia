const canvas = document.getElementById('firmaCanvas');
const ctx = canvas.getContext('2d');
const signatureInput = document.getElementById('signature');
let drawing = false;

// Estilo del trazo
ctx.strokeStyle = '#d4af37';
ctx.lineWidth = 2;

// Convertir coordenadas de pantalla a coordenadas de canvas
function getCanvasPos(e) {
    const rect = canvas.getBoundingClientRect();
    if (e.touches) {
        return {
            x: e.touches[0].clientX - rect.left,
            y: e.touches[0].clientY - rect.top
        };
    } else {
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }
}

// Iniciar dibujo
function startDrawing(e) {
    e.preventDefault();
    drawing = true;
    const pos = getCanvasPos(e);
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
}

// Dibujar trazo
function draw(e) {
    if (!drawing) return;
    e.preventDefault();
    const pos = getCanvasPos(e);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
}

// Detener dibujo
function stopDrawing(e) {
    e.preventDefault();
    if (drawing) {
        ctx.beginPath();  // ← IMPORTANTE para terminar el trazo limpio
    }
    drawing = false;
}

// Borrar firma
function clearSignature() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    signatureInput.value = '';
}

// Verificar si el canvas está vacío
function isCanvasBlank(cnv) {
    const blank = document.createElement('canvas');
    blank.width = cnv.width;
    blank.height = cnv.height;
    return cnv.toDataURL() === blank.toDataURL();
}

// Guardar firma como imagen base64 al enviar formulario
document.getElementById('consentForm').addEventListener('submit', function (e) {
    if (isCanvasBlank(canvas)) {
        e.preventDefault();
        alert('Por favor, firma el consentimiento antes de enviar.');
        return;
    }
    const dataURL = canvas.toDataURL();
    signatureInput.value = dataURL;
});

// Listeners para eventos táctiles y de ratón
canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseout', stopDrawing);

canvas.addEventListener('touchstart', startDrawing, { passive: false });
canvas.addEventListener('touchmove', draw, { passive: false });
canvas.addEventListener('touchend', stopDrawing);

// Exponer función de limpieza globalmente
window.clearSignature = clearSignature;
