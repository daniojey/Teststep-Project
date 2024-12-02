document.addEventListener("DOMContentLoaded", function () {
    // Получаем все чекбоксы с классом answer-checkbox
    const checkboxes = document.querySelectorAll(".correct-answer-checkbox");

    console.log("Инициализация скрипта...");
    console.log("Найдено чекбоксов:", checkboxes.length);

    // Создаем объект для группировки чекбоксов по question.id
    const groupedCheckboxes = {};

    checkboxes.forEach(checkbox => {
        const questionId = checkbox.dataset.questionId;
        console.log(`Чекбокс id: ${checkbox.id}, questionId: ${questionId}`);

        if (!groupedCheckboxes[questionId]) {
            groupedCheckboxes[questionId] = [];
        }
        groupedCheckboxes[questionId].push(checkbox);
    });

    console.log("Группировка чекбоксов по вопросу:", groupedCheckboxes);

    // Добавляем обработчик для каждого вопроса
    Object.values(groupedCheckboxes).forEach(checkboxGroup => {
        checkboxGroup.forEach(checkbox => {
            checkbox.addEventListener("change", function () {
                const answerType = checkbox.dataset.answerType;
                console.log(`Событие change для чекбокса id: ${checkbox.id}, answerType: ${answerType}`);

                if (answerType === "SC") {
                    // Одиночный выбор: снимаем все остальные чекбоксы
                    if (checkbox.checked) {
                        console.log("Одиночный выбор: Снимаем остальные чекбоксы...");
                        checkboxGroup.forEach(cb => {
                            if (cb !== checkbox) {
                                cb.checked = false;
                                console.log(`Снят чекбокс id: ${cb.id}`);
                            }
                        });
                    }
                } else if (answerType === "MC") {
                    // Множественный выбор: не даем выбрать все
                    const checkedCheckboxes = checkboxGroup.filter(cb => cb.checked);
                    console.log("Выбрано чекбоксов:", checkedCheckboxes.length, "из", checkboxGroup.length);

                    if (checkedCheckboxes.length === checkboxGroup.length) {
                        // Если выбраны все, снимаем последний выбранный
                        checkbox.checked = false;
                        alert("Нельзя выбрать все ответы. Оставьте хотя бы один вариант неверным.");
                        console.log(`Снят последний чекбокс id: ${checkbox.id}`);
                    }
                }
            });
        });
    });
});