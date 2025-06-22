document.addEventListener('DOMContentLoaded', () => {
    const questionScores = document.querySelectorAll('#questionScore');
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const messagePopup = document.getElementById('message-popup');


    let timers = new Map()

    questionScores.forEach(question => {
        question.addEventListener('keydown', (e) => {
            if (e.key == 'Enter') {
                e.preventDefault()
                question.blur()
            }
        });

        // question.addEventListener('input', (e) => {
        //     console.log(e.target.value)
        // })

        question.addEventListener('change', () => {
            const questionValue = question.value.replace(',', '.');
            console.log('ПАРСИНГ', parseFloat(questionValue))

            if (parseFloat(questionValue) && parseFloat(questionValue) >= 0 && question.dataset.type === 'SQ' || parseFloat(questionValue) === 0) {

                if (timers.has(question)) {
                    clearTimeout(timers.get(question))
                }

                const formData = new FormData();

                formData.set('score', questionValue)

                let timerId = setTimeout(() => {
                    fetch(`/testes/change_question_score/${question.dataset.ids}/`, 
                        {
                            method: 'POST',
                            body: formData,
                            headers: {
                                'X-CSRFToken': csrfToken
                            }
                        }
                    )
                    .then(response => {
                        if (response.ok) {
                            return response.json()
                        } else {
                            throw new Error('Помилка при відправці данних')
                        }
                    })
                    .then(data => {
                        messagePopup.textContent = data.success;
                        messagePopup.classList.add('active');
                        return data
                    })
                    .catch(error => {
                        messagePopup.textContent = error;
                        messagePopup.classList.add(error)
                    });


                    setTimeout(() => {
                        if (messagePopup.classList.contains('active')) {
                            messagePopup.classList.remove('active');
                        } else if (messagePopup.classList.contains('error')) {
                            messagePopup.classList.remove('error');
                        }
                    }, 5000);
                }, 2200)

                timers.set(question, timerId)
            } else if (question.dataset.type === 'SA') {

                const errorText = "Недопустимий тип питання для зміни балів, зміна балів для питання підтримуется лише при балах за питання, у випадку балів за відповідь змінюйте кількість балів у редакторі відповідей"
                messagePopup.textContent = errorText
                messagePopup.classList.add('error')
                question.value = parseFloat(question.dataset.default.replace(',', '.'))

                setTimeout(() => {
                    if (messagePopup.classList.contains('error')) {
                        messagePopup.classList.remove('error');
                    }


                }, 10000);
            }
        })
    })
})