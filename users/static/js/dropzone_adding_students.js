document.addEventListener('DOMContentLoaded', () => {
    console.log('СКРИПТ загружен')
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadFile');
    const fileName = document.getElementById('fileName');
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const fileForm = document.getElementById('fileForm');

    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        console.log(e.target.value)
        fileName.textContent = e.target.value

        const formData = new FormData()
        formData.append('file', e.target.files[0])

        fetch(fileForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken // Указываем CSRF токен
            }
        })
        .then(response => {
            if (response.ok) {
                console.log(response)
                return response.json();
            } else {
                throw new Error("Ошибка при отправке данных");
            }
        })
        .then(data => {
            console.log("Дата", data)
            console.log("Пользователи", data['users'])
        })
        .catch(error => {
            console.error('Ошибка', error)
        });
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
    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.style.display = 'none';

        if (e.dataTransfer.files.length > 1) {
            alert('Може бути оброблений лише один файл');
            return
        };
        
        const file = e.dataTransfer.files[0];
        console.log(file)
        console.log(file.name)
        console.log(file.type)
        console.log(file.size)
        // const dt = new DataTransfer();
        // for (const file of e.dataTransfer.files) {
        //     console.log(file.name)
        //     dt.items.add(file);
        // }
        // fileInput.files = dt.files;

        console.log(fileForm);
        console.log(fileForm.action);

        console.log(e.dataTransfer.files);

        const formData = new FormData();
        formData.append('file', file);

        formData.append('action', "getUsers");

        fetch(fileForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken // Указываем CSRF токен
            }
        })
        .then(response => {
            if (response.ok) {
                console.log(response)
                return response.json();
            } else {
                throw new Error("Ошибка при отправке данных");
            }
        })
        .then(data => {
            console.log("Дата", data)
            console.log("Пользователи", data['users'])
        })
        .catch(error => {
            console.error('Ошибка', error)
        });
    });

    // Обязательно для корректной работы
    dropZone.addEventListener('dragover', e => e.preventDefault());
});