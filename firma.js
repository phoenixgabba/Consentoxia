let canvas = document.getElementById('firmaCanvas');
let ctx = canvas.getContext('2d');

let drawing = false;

// Función para empezar a dibujar
canvas.addEventListener('touchstart', startDrawing);
canvas.addEventListener('mousedown', startDrawing);

function startDrawing(e) {
    e.preventDefault();  // Evita el comportamiento predeterminado (ej. scrolling en móviles)
    drawing = true;
    ctx.beginPath();
    if (e.type === 'touchstart') {
        ctx.moveTo(e.touches[0].clientX - canvas.offsetLeft, e.touches[0].clientY - canvas.offsetTop);
    } else {
        ctx.moveTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
    }
}

// Función para dibujar mientras se mantiene el dedo o el ratón presionado
canvas.addEventListener('touchmove', draw);
canvas.addEventListener('mousemove', draw);

function draw(e) {
    if (!drawing) return;
    e.preventDefault();
    if (e.type === 'touchmove') {
        ctx.lineTo(e.touches[0].clientX - canvas.offsetLeft, e.touches[0].clientY - canvas.offsetTop);
    } else {
        ctx.lineTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
    }
    ctx.stroke();
}

// Función para detener el dibujo
canvas.addEventListener('touchend', stopDrawing);
canvas.addEventListener('mouseup', stopDrawing);

function stopDrawing() {
    drawing = false;
}

// Función para borrar la firma
function clearSignature() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}
