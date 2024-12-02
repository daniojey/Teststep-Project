document.addEventListener('DOMContentLoaded', function () {
    const uploadButton = document.getElementById('uploadButton');
    const fileInput = document.getElementById('uploadImage');
    const fileNameSpan = document.getElementById('fileName');

    // Открытие диалога выбора файла
    uploadButton.addEventListener('click', () => {
        fileInput.click();
    });

    // Изменение текста кнопки и отображение имени файла
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            const fileName = fileInput.files[0].name;
            const maxLength = 100;
            // Если длина имени файла больше 100 символов, обрезаем его и добавляем многоточие
            const truncatedFileName = fileName.length > maxLength ? fileName.slice(0, maxLength) + '...' : fileName;
            
            uploadButton.textContent = 'Змінити файл';
            fileNameSpan.textContent = `${truncatedFileName}`;
        }
    });
});