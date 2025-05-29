document.addEventListener('DOMContentLoaded', function () {
    const questionTypeSelect = document.getElementById('questionSelect'); // Поле выбора типа вопроса
    const answerTypeSelect = document.getElementById('answerSelect');     // Поле выбора типа ответа

    function toggleAnswerType() {
        if (questionTypeSelect.value === 'MTCH') {
            // Скрываем поле и очищаем значение
            answerTypeSelect.style.display = 'none';
            answerTypeSelect.value = '';
        } else {
            // Показываем поле
            answerTypeSelect.style.display = 'block';
        }
    }

    // Слушаем событие "change" на поле выбора типа вопроса
    questionTypeSelect.addEventListener('change', toggleAnswerType);

    // Инициализация: вызываем функцию при загрузке страницы
    toggleAnswerType();
});