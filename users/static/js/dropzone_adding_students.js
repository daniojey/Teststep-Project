let currentUsersData = null;
const MAX_SIZE_BYTES = 40 * 1024 * 1024;
document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadFile');
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const fileForm = document.getElementById('fileForm');

    const formUsers = document.getElementById('previewForm');
    const formContainer = document.getElementById('previewForm');
    const studentsContainer = document.querySelector('.students-list-container');
    const outBtn = document.querySelector(".out-button");
    const submitBtn = document.querySelector(".submit-btn");
    const loader = document.querySelector(".loader");
    const backgroundContainer = document.querySelector(".students-adding-container");
    const popupError = document.querySelector('.popup-message');


    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });


    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0]
        if (file) {

            if (file.size < MAX_SIZE_BYTES) {
                const data = await fetchData(e, "formSubmit")
                predViewUsers(data['users'])
            } else {
                popupOpen(`Максимальний розмір файлу 40мб, ваш файл ${file.size}`)
            };

        } else {
            popupOpen('Не вказаний файл')
        }
    });


    // Показ дропзоны
    document.addEventListener('dragenter', e => {
        if (e.dataTransfer.types.includes('Files')) {
            dropZone.style.display = 'flex';
        }
    });


    // Скрытие при выходе
    document.addEventListener('dragleave', e => {
        if (e.clientX <= 0 || e.clientY <= 0) {
            dropZone.style.display = 'none';
        }
    });


    // Обработка сброса
    dropZone.addEventListener('drop', async (e) => {
        e.preventDefault();

        const file = e.dataTransfer.files[0];
        if (file) {

            if (file.size < MAX_SIZE_BYTES) {
                const data = await fetchData(e, 'dropFile')
                predViewUsers(data['users'])
            } else {
                popupOpen(`Максимальний розмір файлу 40мб, ваш файл ${file.size}`)
            };

        } else {
            popupOpen('Не вказаний файл')
        };
    });


    // Обязательно для корректной работы
    dropZone.addEventListener('dragover', e => e.preventDefault());


    formUsers.addEventListener('submit', (e) => {
        e.preventDefault();

        if (!currentUsersData) {
            console.log('Нет данных')
            return
        }

        const formData = new FormData();
        formData.set('users', JSON.stringify(currentUsersData));
        formData.set('action', 'createUsers');

        studentsContainer.style.opacity = 0
        setTimeout(() => {
            studentsContainer.innerHTML = '';
            loader.classList.add('active');
            submitBtn.disabled = true;
            outBtn.disabled = true;

        }, 200)


        fetch(fileForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken, // Указываем CSRF токен
                // 'Content-Type': 'application/json',
                // 'X-Action': 'createUsers'
            }
        })
            .then(response => {
                console.log(response)
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error("Помилка при відправці данних");
                }
            })
            .then(data => {
                addCompleteLogo(data['result'])
                console.log(data['result'])
                return data
            })
            .catch(error => {
                console.error(error)
                addErrorLogo()
                popupOpen(error)
            })
    })


    function addCompleteLogo(users) {
        setTimeout(() => {
            loader.classList.remove('active');
            const successLogo = document.createElement('p');
            const successText = document.createElement('p');
            successLogo.classList.add('complete-logo');
            successText.classList.add('result-label');
            successLogo.textContent = '✔';
            successText.textContent = `Створено ${users ? users : 0} користувачів`
            formContainer.appendChild(successLogo);
            formContainer.appendChild(successText);
        }, 1000)
    }

    function addErrorLogo() {
        setTimeout(() => {
            loader.classList.remove('active');
            const successLogo = document.createElement('p');
            const TextError = document.createElement('p');
            successLogo.classList.add('error-logo');
            TextError.classList.add('result-label');
            successLogo.textContent = '✖';
            TextError.textContent = "Помилка при обробці Error(rl-0)"
            formContainer.appendChild(successLogo);
            formContainer.appendChild(TextError);
        }, 1000)
    }

    // function closePreviewWindow() {
    //     backgroundContainer.classList.add('closing');
    //     setTimeout(() => {
    //         backgroundContainer.classList.remove('active', 'closing');
    //         studentsContainer.querySelectorAll('.preview-student-container').forEach(container => container.remove())
    //     }, 600);
    //     fileInput.value = '';
    // }

    function predViewUsers(data) {
        const cross = document.getElementById('cross-preview-container');
        const infoContainer = document.querySelector('.info');

        submitBtn.disabled = false;
        outBtn.disabled = false;
        formContainer.innerHTML = '';
        studentsContainer.style.opacity = 1;
        backgroundContainer.classList.add('active');
        currentUsersData = data


        cross.addEventListener('click', () => {
            backgroundContainer.classList.add('closing');
            setTimeout(() => {
                backgroundContainer.classList.remove('active', 'closing');
                studentsContainer.querySelectorAll('.preview-student-container').forEach(container => container.remove())
            }, 600);
            fileInput.value = '';
        });

        backgroundContainer.addEventListener('click', () => {
            if (event.target === backgroundContainer) {
                backgroundContainer.classList.add('closing');
                setTimeout(() => {
                    backgroundContainer.classList.remove('active', 'closing');
                    studentsContainer.querySelectorAll('.preview-student-container').forEach(container => container.remove())
                }, 600);
                fileInput.value = '';
            }
        });

        outBtn.addEventListener('click', () => {
            backgroundContainer.classList.add('closing');
            setTimeout(() => {
                backgroundContainer.classList.remove('active', 'closing');
                studentsContainer.querySelectorAll('.preview-student-container').forEach(container => container.remove())
            }, 600);
            fileInput.value = '';
        })

        let infoDataLenght = data.length;
        let infoDataValidLenght = 0;

        data.forEach(user => {
            const studentDiv = document.createElement('div');
            studentDiv.classList.add('preview-student-container');

            for (const [key, field] of Object.entries(user)) {
                const studentP = document.createElement('div');

                switch (field.valid) {
                    case true:
                        studentP.classList.add('isvalid');
                        studentP.textContent = field.value;
                        studentDiv.appendChild(studentP);
                        break
                    case false:
                        studentP.classList.add('invalid');
                        studentP.textContent = field.value;
                        studentDiv.appendChild(studentP);
                        break

                }

                if (key == 'overal_valid' && field == false) {
                    studentDiv.classList.add('invalid')
                } else if (key == 'overal_valid' && field == true) {
                    studentDiv.classList.add('valid')
                    infoDataValidLenght += 1;
                }
            }

            infoContainer.textContent = `${infoDataLenght}/${infoDataValidLenght}`
            studentsContainer.appendChild(studentDiv)
        });


    }
});


function popupOpen(message) {
    const popupError = document.querySelector('.popup-message');

    popupError.textContent = message;
    popupError.classList.add("error")
    setTimeout(() => {
        popupError.classList.remove('error')
    }, 5500)
}

async function fetchData(event, action) {
    const fileForm = document.getElementById('fileForm');
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    switch (action) {
        case "formSubmit":
            try {
                const formData = new FormData()
                formData.append('file', event.target.files[0])
                formData.append('action', "getUsers");

                const response = await fetch(fileForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken // Указываем CSRF токен
                    }
                })

                if (!response.ok) {
                    throw new Error("Помилка при відправці данних");
                }

                const data = await response.json();
                console.log("Дата", data);
                console.log("Пользователи", data['users']);

                return data;

            } catch (error) {
                popupOpen(error)
                throw error; // Пробрасываем ошибку дальше
            }

        case "dropFile":
            dropZone.style.display = 'none';

            if (event.dataTransfer.files.length > 1) {
                alert('Може бути оброблений лише один файл');
                return
            };

            const file = event.dataTransfer.files[0];

            try {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('action', "getUsers");

                const response = await fetch(fileForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken // Указываем CSRF токен
                    }
                });

                if (!response.ok) {
                    throw new Error("Помилка при відправці данних");
                };

                const data = await response.json();
                console.log("Дата", data);
                console.log("Пользователи", data['users']);

                return data;

            } catch (error) {
                popupOpen(error)
                throw error;
            }
    }
}