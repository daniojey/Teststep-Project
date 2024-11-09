document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.querySelector(".custom-form");

    loginForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = new FormData(loginForm);

        fetch(loginForm.action, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.json())
        .then(data => {
            const notification = document.createElement("div");
            notification.className = "error-notification";
            const formFields = document.querySelectorAll(".form-control");

            if (data.status === "success") {
                notification.textContent = data.message;
                notification.classList.add("success");
                setTimeout(() => window.location.href = "/", 1000);
            } else {
                notification.textContent = data.message;
                notification.classList.add("error");

                // Добавляем красную границу и мягкую тень ко всем полям
                formFields.forEach(input => {
                    input.style.border = "1px solid #f44336";
                    input.style.boxShadow = "0 0 5px rgba(244, 67, 54, 0.5)";
                    input.style.transition = "border-color 0.3s ease, box-shadow 0.3s ease";
                });
            }

            document.body.appendChild(notification);

            setTimeout(() => {
                notification.classList.add("hide");

                // Убираем красную границу и тень со всех полей
                formFields.forEach(input => {
                    input.style.border = "none";
                    input.style.boxShadow = "none";
                });
            }, 4000);

            setTimeout(() => {
                notification.remove();
            }, 4500);
        })
        .catch(error => console.error("Помилка:", error));
    });
});