document.getElementById('reset-password-button').addEventListener('click', function(event) {
    event.preventDefault();
    const url = this.getAttribute('data-url');  // Получаем URL из data-атрибута
    window.location.href = url;
});

document.getElementById('logout-button').addEventListener('click', function(event) {
    event.preventDefault();
    const url = this.getAttribute('data-url');  // Получаем URL из data-атрибута
    window.location.href = url;
});