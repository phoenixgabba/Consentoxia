let canvas = document.getElementById('firmaCanvas');
let ctx = canvas.getContext('2d');

let drawing = false;

// Ajustar grosor y estilo de línea para que se vea mejor
ctx.lineWidth = 2;
ctx.lineCap = 'round';
ctx.strokeStyle = '#d4af37';

// Función para empezar a dibujar
canvas.addEventListener('touchstart', startDrawing);
canvas.addEventListener('mousedown', startDrawing);

function startDrawing(e) {
    e.preventDefault();
    drawing = true;
    ctx.beginPath();
    if (e.type === 'touchstart') {
        const touch = e.touches[0];
        ctx.moveTo(touch.clientX - canvas.offsetLeft, touch.clientY - canvas.offsetTop);
    } else {
        ctx.moveTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
    }
}

// Dibujar mientras toca o mueve ratón
canvas.addEventListener('touchmove', draw);
canvas.addEventListener('mousemove', draw);

function draw(e) {
    if (!drawing) return;
    e.preventDefault();
    if (e.type === 'touchmove') {
        const touch = e.touches[0];
        ctx.lineTo(touch.clientX - canvas.offsetLeft, touch.clientY - canvas.offsetTop);
    } else {
        ctx.lineTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
    }
    ctx.stroke();
}

// Parar dibujo
canvas.addEventListener('touchend', stopDrawing);
canvas.addEventListener('mouseup', stopDrawing);

function stopDrawing() {
    drawing = false;
}

// Borrar firma
function clearSignature() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}
