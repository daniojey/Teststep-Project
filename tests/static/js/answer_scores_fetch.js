document.addEventListener('DOMContentLoaded', () => {
    const answerScores = document.querySelectorAll("#answerScore");
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const messagePopup = document.getElementById('message-popup');

    function isPositiveIntegerString(str) {
        return /^\d+$/.test(str); // без поддержки отрицательных чисел
    }

    let timers = new Map()

    answerScores.forEach(answer => {
        answer.addEventListener('keydown', (e) => {
            if (e.key == 'Enter') {
                e.preventDefault()
                answer.blur();
            }
        });

        answer.addEventListener('change', () => {
            if (parseInt(answer.value, 10) && isPositiveIntegerString(answer.value)) {
                console.log('ПРОВЕРКА')

                if (timers.has(answer)) {
                    clearTimeout(timers.get(answer));
                }
                
                const formData = new FormData();
                // formData.set('score', "bob")
                formData.set('score', answer.value)
                formData.set('type', answer.dataset.type)

                let timerId = setTimeout(() => {
                    fetch(`/testes/change_answer_score/${answer.dataset.ids}/`, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': csrfToken // Указываем CSRF токен
                        }
                    })
                    .then(response => {
                        if (response.ok) {
                            return response.json(); // Ожидаем JSON-ответ от сервера
                        } else {
                            throw new Error('Помилка при отриманні даних ');
                        }
                    })
                    .then(data => {
                        messagePopup.textContent = data.success;
                        messagePopup.classList.add('active');
                        return data
                    })
                    .catch(error => {
                        messagePopup.textContent = error;
                        messagePopup.classList.add('error');
                    });


                    setTimeout(() => {
                        if (messagePopup.classList.contains('active')) {
                            messagePopup.classList.remove('active');
                        } else if (messagePopup.classList.contains('error')) {
                            messagePopup.classList.remove('error');
                        }
                    }, 5000);

                }, 2200)

                timers.set(answer, timerId)
            } else {

            }
        })
    })
})