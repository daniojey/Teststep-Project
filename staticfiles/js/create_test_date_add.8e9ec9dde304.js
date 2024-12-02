document.addEventListener("DOMContentLoaded", function () {
    const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
    const dateInput = document.querySelector("#date-input");
    const customIcon = document.querySelector(".calendar-icon");

    if (isMobile) {
        // Для мобильных устройств: используем стандартный календарь
        dateInput.type = "date"; // Меняем тип на date для мобильных устройств
        dateInput.placeholder = "Оберіть дату"; // Плейсхолдер для мобильных

        customIcon.style.display = "none";

        customIcon.addEventListener("click", function () {
            dateInput.click(); // Программно вызываем клик на нативное поле
        });
    } else {
        // Для ПК: инициализируем Flatpickr
        flatpickr(dateInput, {
            enableTime: false,
            dateFormat: "Y-m-d", // Формат, совместимый с Django
            disableMobile: true, // Отключаем мобильный интерфейс
        });

        // Обработчик клика на кастомную кнопку
        customIcon.addEventListener("click", function () {
            dateInput._flatpickr.open(); // Открываем Flatpickr
        });
    }
});