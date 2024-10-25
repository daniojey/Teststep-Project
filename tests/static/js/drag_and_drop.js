
// Функция для обработки начала перетаскивания
function drag(event) {
    var data = event.target.getAttribute('data-right-item');
    if (data) {
        event.dataTransfer.setData("text", event.target.id);  // Передаём ID элемента
        console.log("Начато перетаскивание элемента с данными:", data);
    } else {
        console.error("Ошибка: атрибут data-right-item пустой!");
    }
}

// Функция для разрешения сброса элемента
function allowDrop(event) {
    event.preventDefault();  // Останавливаем стандартное поведение браузера
}

// Функция для обработки сброса элемента в dropzone
function drop(event) {
    event.preventDefault();

    // Получаем ID элемента, который был перетащен
    var draggedElementId = event.dataTransfer.getData("text");
    var draggedElement = document.getElementById(draggedElementId);

    if (draggedElement) {
        var dropzone = event.target;

        // Перемещаем перетаскиваемый элемент в новую зону
        dropzone.appendChild(draggedElement);

        // Получаем значения левого и правого элемента
        var leftBlockId = dropzone.getAttribute('data-left-item');  // Получаем идентификатор левого элемента
        var rightBlockValue = draggedElement.getAttribute('data-right-item');  // Получаем значение правого элемента

        console.log("Сопоставлены элементы:", leftBlockId, "с", rightBlockValue);

        // Обновляем скрытое поле с результатом сопоставления
        var matchingInput = document.getElementById('answer_' + leftBlockId);  // Используем идентификатор левого элемента
        if (matchingInput) {
            matchingInput.value = rightBlockValue;
            console.log("Обновлено скрытое поле для POST-запроса:", matchingInput);
        } else {
            console.error("Не удалось найти скрытое поле для:", leftBlockId);
        }
    } else {
        console.error("Перетаскиваемый элемент не найден:", draggedElementId);
    }
}