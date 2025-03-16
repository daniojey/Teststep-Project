// Обновленный JavaScript код
async function uploadImage(input) {
    console.log('Запуск');
    try {
        var formData = new FormData();
        formData.append('image', input.files[0]);
        
        const uploadUrl = document.querySelector('.upload-icon').dataset.uploadUrl;
        const csrfToken = document.querySelector('.upload-icon').dataset.csrfToken;
        const messageSuccess = document.getElementById('notification')
        
        const response = await fetch(uploadUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });


        const data = await response.json();

        if (data.success) {
            messageSuccess.textContent = 'Фото успішно збережено!'
            messageSuccess.classList.add('show-message');
            messageSuccess.style.display = 'flex';
            messageSuccess.style.opacity = '1';
            
            setTimeout(() => {
                messageSuccess.style.opacity = '0';
            }, 6000);

            setTimeout(() => {
                messageSuccess.style.display = 'none';
                messageSuccess.classList.remove('show-message');
            }, 7000);
            
            document.getElementById('profile-image').src = data.image_url;
            
        } else  {
            console.error('Ошибка при загрузке изображения:', data.error);
        };
        
    } catch {
        const messageSuccess = document.getElementById('notification')

        messageSuccess.classList.add('show-error-message');
        messageSuccess.textContent = 'Помилка при збереженні фото'
        messageSuccess.style.display = 'flex';
        messageSuccess.style.opacity = '1';
            
        setTimeout(() => {
                messageSuccess.style.opacity = '0';
        }, 6000);

        setTimeout(() => {
                messageSuccess.style.display = 'none';
                messageSuccess.classList.remove('show-error-message');
        }, 7000);
    };
}
//         fetch(uploadUrl, {
//             method: 'POST',
//             headers: {
//             'X-CSRFToken': csrfToken
//         },
//         body: formData
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.success) {
//             document.getElementById('profile-image').src = data.image_url;
//         } else {
//             console.error('Ошибка при загрузке изображения:', data.error);
//         }
//     })
//     .catch(error => console.error('Ошибка при отправке запроса:', error));
// }