document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("registrationForm");
    const emailInput = document.getElementById("id_email");
    const password1Input = document.getElementById("id_password1");
    const password2Input = document.getElementById("id_password2");
    const submitBtn = document.getElementById("submit-btn");
    const checkbox = document.getElementById("agreement");
    
    const errorMessagesContainer = document.getElementById("errorMessagesContainer");

    function showError(message, field) {
        // Устанавливаем подсветку поля с ошибкой
        field.style.border = "1px solid #f44336";
        field.style.transition = "border-color 0.3s ease, box-shadow 0.3s ease";
        
        // Проверяем, нет ли уже такого сообщения об ошибке
        if (!document.querySelector(`.error-message[data-field="${field.id}"]`)) {
            const errorDiv = document.createElement("div");
            errorDiv.classList.add("error-message");
            errorDiv.setAttribute("data-field", field.id);
            errorDiv.textContent = message;
            errorMessagesContainer.appendChild(errorDiv);
        }
    }

    function clearError(field) {
        // Убираем подсветку с поля, если ошибка исправлена
        field.style.border = "none";
        field.style.boxShadow = "none";
        
        // Удаляем сообщение об ошибке, если оно есть
        const errorDiv = document.querySelector(`.error-message[data-field="${field.id}"]`);
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    function validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function validateForm() {
        let isValid = true;

        if (!validateEmail(emailInput.value) && emailInput.value !== "") {
            showError("Введите корректный email", emailInput);
            isValid = false;
        } else {
            clearError(emailInput);
        }
        
        if (password1Input.value.length > 0 && password1Input.value.length < 8) {
            showError("Пароль должен быть не менее 8 символов", password1Input);
            isValid = false;
        } else {
            clearError(password1Input);
        }

        if (password1Input.value !== password2Input.value && password2Input.value !== "") {
            showError("Пароли не совпадают", password2Input);
            isValid = false;
        } else {
            clearError(password2Input);
        }

        return isValid;
    }

    function handleFocus(field) {
        // Если поле с ошибкой, оставляем красную рамку при фокусировке
        const errorDiv = document.querySelector(`.error-message[data-field="${field.id}"]`);
        if (errorDiv) {
            field.style.border = "1px solid #f44336";
            
            
        }
    }

    password1Input.addEventListener("focus", function () {
        handleFocus(password1Input);
        if (password1Input.value.length < 8 && password1Input.value !== "") {
            showError("Пароль должен быть не менее 8 символов", password1Input);
        }
    });

    emailInput.addEventListener("focus", function () {
        handleFocus(emailInput);
        if (!validateEmail(emailInput.value) && emailInput.value !== "") {
            showError("Введите корректный email", emailInput);
        }
    });

    password2Input.addEventListener("focus", function () {
        handleFocus(password2Input);
        if (password1Input.value !== password2Input.value && password2Input.value !== "") {
            showError("Пароли не совпадают", password2Input);
        }
    });

    password1Input.addEventListener("input", () => validateForm());
    password2Input.addEventListener("input", () => validateForm());
    emailInput.addEventListener("input", () => validateForm());

    form.addEventListener("submit", function (event) {
        if (!validateForm()) {
            event.preventDefault();
        }
    });

    checkbox.addEventListener("change", function () {
        submitBtn.disabled = !checkbox.checked;
    });
});   