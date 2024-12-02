// Функция для открытия модального окна
function openModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.classList.add("show");
}

// Функция для закрытия модального окна
function closeModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.classList.remove("show");
}

// Закрытие модального окна при клике вне его области
window.onclick = function(event) {
    var modals = document.getElementsByClassName("modal");
    for (let i = 0; i < modals.length; i++) {
        if (event.target == modals[i]) {
            modals[i].classList.remove("show");
        }
    }
}