document.addEventListener('DOMContentLoaded', function () {
    // Функция для удаления заглушки
    function removePlaceholder(optionElement) {
        if (optionElement && optionElement.value === '') {
            optionElement.remove();
        }
    }

    // Найти все элементы <select> в форме
    const selectFields = document.querySelectorAll('select');

    // Добавить обработчик события изменения для каждого select
    selectFields.forEach(function (select) {
        // Пропускаем поле group
        if (select.id === 'id_group') return;

        select.addEventListener('change', function () {
            const selectedOption = select.options[select.selectedIndex];
            const placeholderOption = select.querySelector('option[value=""]');

            // Если выбрано что-то кроме заглушки, удаляем заглушку
            if (selectedOption && placeholderOption) {
                removePlaceholder(placeholderOption);
            }
        });
    });
});