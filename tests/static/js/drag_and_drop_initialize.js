// Начало перетаскивания
function drag(event) {
    var data = event.target.getAttribute('data-right-item');
    if (data) {
        event.dataTransfer.setData("text", event.target.id);

        // Проверяем, что у элемента есть атрибут data-original-parent
        var originalParent = event.target.getAttribute("data-original-parent");
        if (!originalParent) {
            console.error("Не удалось найти атрибут data-original-parent для элемента:", event.target.id);
        }

        console.log("Начато перетаскивание элемента с данными:", data);
    } else {
        console.error("Ошибка: атрибут data-right-item пустой!");
    }
}

// Разрешение сброса элемента
function allowDrop(event) {
    event.preventDefault();
}

// Сброс элемента в dropzone
function drop(event) {
    event.preventDefault();

    var draggedElementId = event.dataTransfer.getData("text");
    var draggedElement = document.getElementById(draggedElementId);

    if (draggedElement) {
        var dropzone = event.target.closest(".dropzone");

        if (dropzone) {
            // Проверка на наличие элемента в dropzone
            var existingElement = dropzone.querySelector(".right-item");

            if (existingElement) {
                // Возвращаем существующий элемент в его исходный контейнер
                resetElementPosition(existingElement);
            }

            // Перемещаем перетаскиваемый элемент в dropzone
            dropzone.appendChild(draggedElement);

            // Сбрасываем стили смещения
            draggedElement.style.position = 'relative';
            draggedElement.style.left = '0';
            draggedElement.style.top = '0';

            // Обновляем скрытое поле
            var leftBlockId = dropzone.getAttribute('data-left-item');
            var rightBlockValue = draggedElement.getAttribute('data-right-item');
            var matchingInput = document.getElementById('answer_' + leftBlockId);

            if (matchingInput) {
                matchingInput.value = rightBlockValue;
                console.log("Обновлено скрытое поле для POST-запроса:", matchingInput);
            } else {
                console.error("Не удалось найти скрытое поле для:", leftBlockId);
            }
        } else {
            console.error("Не удалось найти родительский элемент dropzone.");
        }
    } else {
        console.error("Перетаскиваемый элемент не найден:", draggedElementId);
    }
}

// Возвращение элемента на исходную позицию
function resetElementPosition(element) {
    var originalParentId = element.getAttribute("data-original-parent");
    if (originalParentId) {
        var originalParent = document.getElementById(originalParentId);
        if (originalParent) {
            originalParent.appendChild(element);
        } else {
            console.error("Не удалось найти исходный контейнер для элемента:", originalParentId);
        }
    } else {
        console.error("Атрибут data-original-parent отсутствует у элемента:", element.id);
    }

    // Сброс позиции элемента
    element.style.position = 'relative';
    element.style.left = '0';
    element.style.top = '0';
}
