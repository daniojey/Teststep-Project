document.addEventListener("DOMContentLoaded", function () {
    const lazyBackgrounds = document.querySelectorAll(".test-item[data-bg]");

    // Проверяем, поддерживает ли браузер Intersection Observer
    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const bgUrl = element.getAttribute("data-bg");
                    if (bgUrl) {
                        element.style.backgroundImage = `url('${bgUrl}')`;
                        element.removeAttribute("data-bg"); // Удаляем атрибут после установки
                        observer.unobserve(element); // Останавливаем наблюдение
                    }
                }
            });
        });

        lazyBackgrounds.forEach((bg) => observer.observe(bg));
    } else {
        // Если Intersection Observer не поддерживается, загружаем сразу
        lazyBackgrounds.forEach((bg) => {
            const bgUrl = bg.getAttribute("data-bg");
            if (bgUrl) {
                bg.style.backgroundImage = `url('${bgUrl}')`;
                bg.removeAttribute("data-bg");
            }
        });
    }
});