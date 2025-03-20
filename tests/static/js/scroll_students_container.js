document.addEventListener("DOMContentLoaded", () => {
    const baseContainer = document.querySelector('.students-base-container'); // Ограничивающий контейнер
    const students = document.querySelector('.students-container'); // Двигающийся элемент

    if (!baseContainer || !students) {
        console.error("Элементы не найдены. Проверьте наличие классов 'students-base-container' и 'students-container'.");
        return;
    }

    // Функция для проверки и активации скрипта в зависимости от ширины окна
    const checkWindowWidth = () => {
        if (window.innerWidth <= 1000) {
            // console.log("Скрипт отключен для ширины окна <= 1000px.");
            window.removeEventListener('scroll', updatePosition); // Отключаем обработчик скролла
            // Возвращаем элемент в обычное положение
            students.style.position = 'static'; // Сбрасываем позицию
            students.style.top = ''; // Сбрасываем отступы
        } else {
            // console.log("Скрипт активирован для ширины окна > 1000px.");
            updatePosition();
            window.addEventListener('scroll', updatePosition); // Включаем обработчик скролла
        }
    };

    // Функция обновления позиции students-container
    const updatePosition = () => {
        const containerRect = baseContainer.getBoundingClientRect(); // Размеры ограничивающего контейнера
        const offsetTop = containerRect.top; // Верхняя граница относительно окна
        const offsetBottom = containerRect.bottom; // Нижняя граница относительно окна

        // Проверяем, находится ли верхняя граница в зоне видимости
        if (offsetTop < 0 && offsetBottom > students.offsetHeight) {
            // Фиксируем элемент в пределах видимой области
            students.style.position = 'fixed';
            students.style.top = '10px'; // Отступ сверху (можно настроить)
        } else if (offsetTop >= 0) {
            // Возвращаем к исходному состоянию (в начале прокрутки)
            students.style.position = 'absolute';
            students.style.top = '0';
        } else if (offsetBottom <= students.offsetHeight) {
            // Устанавливаем положение на нижней границе
            students.style.position = 'absolute';
            students.style.top = `${baseContainer.offsetHeight - students.offsetHeight}px`;
        } else {
            students.style.position = 'absolute';
        }
    };

    // Проверка ширины окна при загрузке страницы
    checkWindowWidth();

    // Обновляем проверку при изменении размера окна
    window.addEventListener('resize', checkWindowWidth);

    console.log("Скрипт успешно загружен и работает.");
});
