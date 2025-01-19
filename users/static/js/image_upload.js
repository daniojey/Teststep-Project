// Обновленный JavaScript код
function uploadImage(input) {
    var formData = new FormData();
    formData.append('image', input.files[0]);

    const uploadUrl = document.querySelector('.upload-icon').dataset.uploadUrl;
    const csrfToken = document.querySelector('.upload-icon').dataset.csrfToken;

    fetch(uploadUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('profile-image').src = data.image_url;
        } else {
            console.error('Ошибка при загрузке изображения:', data.error);
        }
    })
    .catch(error => console.error('Ошибка при отправке запроса:', error));
}