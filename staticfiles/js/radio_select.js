document.addEventListener("DOMContentLoaded", function() {
    // Находим все элементы label, которые обертывают кастомные радио-кнопки
    const customRadios = document.querySelectorAll('.custom-radio');

    customRadios.forEach(radio => {
        radio.addEventListener('click', function() {
            // Удаляем класс "active" со всех кастомных радио-кнопок
            customRadios.forEach(r => r.classList.remove('active'));
            
            // Добавляем класс "active" к выбранной радио-кнопке
            this.classList.add('active');
            
            // Находим внутри скрытый input[type="radio"] и "выбираем" его
            const input = this.querySelector('input[type="radio"]');
            input.checked = true;
        });
    });
});