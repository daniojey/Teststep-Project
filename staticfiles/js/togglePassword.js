// togglePassword.js

document.addEventListener("DOMContentLoaded", function() {
    const togglePasswordVisibility = (eyeIcon, passwordInput) => {
        const eyeOpenIcon = eyeIcon.getAttribute('data-eye-open');
        const eyeClosedIcon = eyeIcon.getAttribute('data-eye-closed');

        eyeIcon.onclick = function() {
            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                eyeIcon.src = eyeClosedIcon; // Меняем иконку на открытую
            } else {
                passwordInput.type = "password";
                eyeIcon.src = eyeOpenIcon; // Меняем иконку на закрытую
            }
        };
    };

    const eyeIcon1 = document.getElementById('eyeicon');
    const passwordInput1 = document.getElementById('id_password1');

    const eyeIcon2 = document.getElementById('eyeicon2');
    const passwordInput2 = document.getElementById('id_password2');

    // Применяем функцию для каждого поля ввода пароля
    togglePasswordVisibility(eyeIcon1, passwordInput1);
    togglePasswordVisibility(eyeIcon2, passwordInput2);
});