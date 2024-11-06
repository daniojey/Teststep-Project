let mediaRecorder;
let recordedChunks = [];

function toggleRecording(questionId) {
    const audiocontainer = document.querySelector('.audio-base-container');
    const microphoneIcon = document.getElementById('microphoneIcon');
    
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        // Начинаем запись
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.ondataavailable = function (event) {
                    if (event.data.size > 0) {
                        recordedChunks.push(event.data);
                    }
                };
                
                mediaRecorder.onstop = function () {
                    let blob = new Blob(recordedChunks, { type: 'audio/webm' });
                    let reader = new FileReader();
                    
                    // Преобразуем в Base64 и сохраняем в скрытое поле формы
                    reader.onloadend = function () {
                        document.getElementById(`id_audio_answer_${questionId}`).value = reader.result;
                    };
                    reader.readAsDataURL(blob);

                    // Очищаем записи для следующей сессии
                    recordedChunks = [];
                    console.log("Запись завершена и сохранена.");
                };

                // Начинаем запись
                mediaRecorder.start();
                audiocontainer.style.backgroundColor = 'red';
                console.log("Запись началась...");
            })
            .catch(error => console.error("Ошибка доступа к микрофону:", error));
        
    } else if (mediaRecorder.state === 'recording') {
        // Останавливаем запись
        mediaRecorder.stop();
        audiocontainer.style.backgroundColor = 'white'; // Возвращаем цвет
        console.log("Запись остановлена...");
    }
}
