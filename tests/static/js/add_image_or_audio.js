document.addEventListener('DOMContentLoaded', function () {
    // Получаем элементы формы
    const questionTypeField = document.getElementById('id_question_type');
    const imageButton = document.getElementById('uploadImageButton');
    const audioButton = document.getElementById('uploadAudioButton');
    const imageInput = document.getElementById('uploadImage');
    const audioInput = document.getElementById('uploadAudio');
    const imageField = document.getElementById('image-field');
    const audioField = document.getElementById('audio-field');
    const fileNameSpan = document.getElementById('fileName');

    // Функция для обновления видимости полей
    function updateFieldVisibility() {
        const selectedType = questionTypeField.value;

        // Скрываем/показываем поля
        if (selectedType === 'IMG') {
            imageField.style.display = 'flex';
            audioField.style.display = 'none';
            clearFileInput(audioInput); // Очистка поля аудио при переключении на изображение
        } else if (selectedType === 'AUD') {
            imageField.style.display = 'none';
            audioField.style.display = 'flex';
            clearFileInput(imageInput); // Очистка поля изображения при переключении на аудио
        } else {
            imageField.style.display = 'none';
            audioField.style.display = 'none';
            clearFileInput(imageInput); // Очистка всех файлов, если тип не IMG или AUD
            clearFileInput(audioInput);
        }
    }

    // Функция для очистки поля файла
    function clearFileInput(fileInput) {
        if (fileInput) {
            fileInput.value = ''; // Очищает выбранный файл
            fileNameSpan.textContent = ''; // Очищает отображение имени файла
            imageButton.textContent = 'Додати фото';
            audioButton.textContent = 'Додати аудіо';
        }
    }

    // Инициализация состояния
    updateFieldVisibility();

    // Открытие диалога выбора файла
    imageButton.addEventListener('click', () => {
        imageInput.click();
    });

    // Открытие диалога выбора файла
    audioButton.addEventListener('click', () => {
        audioInput.click();
    });

    // Обработчик изменения поля изображения
    imageInput.addEventListener('change', () => {
        if (imageInput.files.length > 0) {
            const fileName = imageInput.files[0].name;
            const maxLength = 100;
            // Если длина имени файла больше 100 символов, обрезаем его и добавляем многоточие
            const truncatedFileName = fileName.length > maxLength ? fileName.slice(0, maxLength) + '...' : fileName;

            imageButton.textContent = 'Змінити файл';
            fileNameSpan.textContent = `${truncatedFileName}`;
        }
    });

    // Обработчик изменения поля аудио
    audioInput.addEventListener('change', () => {
        if (audioInput.files.length > 0) {
            const fileName = audioInput.files[0].name;
            const maxLength = 100;
            // Если длина имени файла больше 100 символов, обрезаем его и добавляем многоточие
            const truncatedFileName = fileName.length > maxLength ? fileName.slice(0, maxLength) + '...' : fileName;

            audioButton.textContent = 'Змінити файл';
            fileNameSpan.textContent = `${truncatedFileName}`;
        }
    });

    // Обработчик изменения поля типа вопроса
    questionTypeField.addEventListener('change', updateFieldVisibility);
});