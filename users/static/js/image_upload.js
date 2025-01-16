function uploadImage(input) {
    var formData = new FormData();
    formData.append('image', input.files[0]);

    // Отправляем запрос с помощью Fetch API
    fetch("{% url 'users:profile_image_upload' %}", {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Обновляем изображение профиля без перезагрузки страницы
            document.getElementById('profile-image').src = data.image_url;
        } else {
            console.error('Ошибка при загрузке изображения:', data.error);
        }
    })
    .catch(error => console.error('Ошибка при отправке запроса:', error));
}