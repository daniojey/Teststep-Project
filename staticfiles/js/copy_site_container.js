document.addEventListener("DOMContentLoaded", () => {
    const mainTestContainer = document.querySelector('.main-test-container');
    const baseStudentsContainer = document.querySelector('.students-base-container');

    if (!mainTestContainer || !baseStudentsContainer) {
        console.error("Не найдены элементы main-test-container или students-base-container.");
        return;
    }

    // Функция для синхронизации высоты
    const syncHeight = () => {
        // console.log("Ширина окна: ", window.innerWidth); // Логируем ширину окна
        if (window.innerWidth <= 1000) {
            // console.log("Устанавливаем фиксированную высоту 200px");
            baseStudentsContainer.style.height = '200px';
            baseStudentsContainer.style.minHeight = '0'; // Убираем min-height
        } else {
            const testContainerHeight = mainTestContainer.offsetHeight;
            // console.log("Синхронизируем высоту с mainTestContainer: ", testContainerHeight);
            baseStudentsContainer.style.minHeight = `${testContainerHeight}px`; // Восстанавливаем min-height, если нужно
        }
    };

    // Вызываем при загрузке
    syncHeight();

    // Если содержимое динамическое, следим за изменением высоты
    const observer = new ResizeObserver(syncHeight);
    observer.observe(mainTestContainer);

    // Обновляем высоту при изменении размера окна
    window.addEventListener('resize', syncHeight);
});
