// Функция для открытия модального окна
function openModal(element) {
    const itemType = element.dataset.type; // Получаем тип элемента (test или question)
    const itemId = element.dataset.id; // Получаем ID элемента

    console.log(itemType)
    console.log(itemId)
    let url;

    if (itemType === 'test') {
        // URL для удаления теста
        url = `/testes/delete_test/${itemId}`; // Убедись, что маршрут соответствует urls.py
    } else if (itemType === 'question') {
        const questionType = element.dataset.questionType; // Получаем тип вопроса
        // URL для удаления вопроса
        if (questionType === 'MTCH') {
            url = `/testes/${itemId}/delete_matching_pair/`;
        } else {
            url = `/testes/delete_question/${itemId}/`;
        }
    }

    // Создаём модальное окно
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.id = `modal-${itemId}`;

    modal.innerHTML = `
        <div class="modal-content">
            <span class="close" onclick="closeModal('${modal.id}')">&times;</span>
            <h2>Видалити ${itemType === 'test' ? 'тест' : 'питання'}?</h2>
            <p>Ви впевненні що бажаєте видалити ${itemType === 'test' ? 'тест' : 'питання'}? Цю дію неможливо буде відмінити.</p>
            <form method="post" action="${url}">
                <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrfToken()}">
                <button type="submit" class="confirm-btn">Видалити</button>
                <button type="button" class="cancel-btn" onclick="closeModal('${modal.id}')">Відмінити</button>
            </form>
        </div>
    `;

    // Добавляем модальное окно в DOM
    document.body.appendChild(modal);
}

// Функция для закрытия модального окна
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        modal.remove(); // Удаляем модальное окно из DOM
    }
}

// Получаем CSRF-токен из cookie
function getCsrfToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(`${name}=`)) {
            return cookie.substring(name.length + 1);
        }
    }
    return '';
}

// Закрытие модального окна при клике вне его области
window.onclick = function (event) {
    const modals = document.getElementsByClassName('modal');
    for (let i = 0; i < modals.length; i++) {
        if (event.target === modals[i]) {
            modals[i].classList.remove('show');
            modals[i].remove(); // Удаляем модальное окно из DOM
        }
    }
};