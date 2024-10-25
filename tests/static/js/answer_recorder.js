
let mediaRecorder;
let recordedChunks = [];

function startRecording(questionId) {
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
                let url = URL.createObjectURL(blob);
                let audioElement = document.getElementById('audio_playback_' + questionId);
                audioElement.src = url;

                // Преобразуем в base64 и сохраняем в скрытое поле формы
                let reader = new FileReader();
                reader.onloadend = function () {
                    document.getElementById('id_audio_answer_' + questionId).value = reader.result;  // input id с префиксом 'id_'
                }
                reader.readAsDataURL(blob);

                recordedChunks = [];
            };
            mediaRecorder.start();
            document.querySelector('button[onclick="startRecording(' + questionId + ')"]').disabled = true;
            document.querySelector('button[onclick="stopRecording(' + questionId + ')"]').disabled = false;
        })
        .catch(error => {
            console.error("Error accessing microphone:", error);
        });
}

function stopRecording(questionId) {
    mediaRecorder.stop();
    document.querySelector('button[onclick="startRecording(' + questionId + ')"]').disabled = false;
    document.querySelector('button[onclick="stopRecording(' + questionId + ')"]').disabled = true;
}
