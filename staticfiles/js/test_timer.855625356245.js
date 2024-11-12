document.addEventListener("DOMContentLoaded", function () {
    // Получаем значение времени из скрытого поля в HTML
    var countDownDuration = parseInt(document.getElementById("remaining_time").value, 10) * 1000;

    if (isNaN(countDownDuration) || countDownDuration <= 0) {
        console.error("Invalid or missing duration:", countDownDuration);
    } else {
        var timer = setInterval(function () {
            if (countDownDuration <= 0) {
                clearInterval(timer);
                document.getElementById("remaining_time").value = 0;
                document.getElementById("test-form").submit();  // Автоматическая отправка формы
            } else {
                // Рассчитываем часы, минуты и секунды
                var hours = Math.floor((countDownDuration % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((countDownDuration % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((countDownDuration % (1000 * 60)) / 1000);

                // Форматируем отображение времени
                var display = (hours > 0 ? hours + "h " : "") + minutes + "m " + seconds + "s ";
                document.getElementById('timer').innerText = display;

                // Уменьшаем время на одну секунду
                countDownDuration -= 1000;

                // Обновляем скрытое поле для отправки времени на сервер
                document.getElementById("remaining_time").value = Math.max(countDownDuration / 1000, 0);
            }
        }, 1000);
    }
});