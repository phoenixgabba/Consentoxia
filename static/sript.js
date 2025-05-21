
document.getElementById('consentForm').addEventListener('submit', function(event) {
    const name = document.getElementById('full_name').value;
    const signature = document.getElementById('signature').value;

    if (name !== signature) {
        event.preventDefault();
        alert('La firma no coincide con el nombre completo.');
    }
});
