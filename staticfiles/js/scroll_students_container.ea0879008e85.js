document.addEventListener("DOMContentLoaded", () => {
    const baseContainer = document.querySelector('.students-base-container'); // Ограничивающий контейнер
    const students = document.querySelector('.students-container'); // Двигающийся элемент

    if (!baseContainer || !students) {
        console.error("Элементы не найдены. Проверьте наличие классов 'students-base-container' и 'students-container'.");
        return;
    }

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
        }
    };

    // Обновляем позицию на скролле
    window.addEventListener('scroll', updatePosition);

    console.log("Скрипт успешно загружен и работает.");
});