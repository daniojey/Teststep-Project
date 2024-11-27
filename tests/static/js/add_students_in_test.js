document.addEventListener('DOMContentLoaded', () => {
    // Получаем форму
    const form = document.getElementById('studentForm');
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    // Навешиваем обработчик события на каждый чекбокс
    form.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            // Формируем данные формы
            const formData = new FormData(form);

            // Отправляем данные через fetch
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken // Указываем CSRF токен
                }
            })
            .then(response => {
                if (response.ok) {
                    return response.json(); // Ожидаем JSON-ответ от сервера
                } else {
                    throw new Error('Ошибка при отправке данных');
                }
            })
            .then(data => {
                console.log('Успех:', data); // Обработка успешного ответа
            })
            .catch(error => {
                console.error('Ошибка:', error); // Обработка ошибок
            });
        });
    });
});