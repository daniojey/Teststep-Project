document.addEventListener("DOMContentLoaded", () => {
    const mainTestContainer = document.querySelector('.main-test-container');
    const baseStudentsContainer = document.querySelector('.students-base-container');

    if (!mainTestContainer || !baseStudentsContainer) {
        console.error("Не найдены элементы main-test-container или students-base-container.");
        return;
    }

    // Функция для синхронизации высоты
    const syncHeight = () => {
        const testContainerHeight = mainTestContainer.offsetHeight;
        baseStudentsContainer.style.height = `${testContainerHeight}px`;
    };

    // Вызываем при загрузке
    syncHeight();

    // Если содержимое динамическое, следим за изменением высоты
    const observer = new ResizeObserver(syncHeight);
    observer.observe(mainTestContainer);
});