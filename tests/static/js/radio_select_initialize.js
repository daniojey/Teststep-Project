document.addEventListener("DOMContentLoaded", function() {
    // Находим все элементы label, которые обертывают кастомные радио-кнопки
    const customRadios = document.querySelectorAll('.custom-radio');

    customRadios.forEach(radio => {
        // Если радио-кнопка уже выбрана (например, предзаполненное значение), добавляем класс "active"
        const input = radio.querySelector('input[type="radio"]');
        if (input.checked) {
            radio.classList.add('active');
        }

        // Обрабатываем событие клика
        radio.addEventListener('click', function() {
            // Удаляем класс "active" со всех кастомных радио-кнопок
            customRadios.forEach(r => r.classList.remove('active'));
            
            // Добавляем класс "active" к выбранной радио-кнопке
            this.classList.add('active');
            
            // Находим внутри скрытый input[type="radio"] и "выбираем" его
            input.checked = true;
        });
    });
});