//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; // Stream from getUserMedia()
var rec; // Recorder.js object
var input; // MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not available
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; // Audio context to help us record

// Function to toggle recording
function toggleRecording(questionId) {
    const audioContainer = document.querySelector('.audio-base-container');
    const microphoneIcon = document.getElementById('microphoneIcon');

    if (!rec || !rec.recording) {
        // Start recording
        navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
            console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

            // Create an audio context after getUserMedia is called
            audioContext = new AudioContext();

            // Assign stream to gumStream for later use
            gumStream = stream;

            // Create the input point from the audio stream
            input = audioContext.createMediaStreamSource(stream);

            // Initialize the Recorder.js object
            rec = new Recorder(input, { numChannels: 1 });

            // Start recording
            rec.record();
            audioContainer.style.backgroundColor = 'red'; // Indicate recording is active
            console.log("Recording started");
        }).catch(function (err) {
            console.error("Error accessing microphone:", err);
        });
    } else {
        // Stop recording
        rec.stop();
        gumStream.getAudioTracks()[0].stop(); // Stop microphone access
        audioContainer.style.backgroundColor = 'white'; // Reset background color
        console.log("Recording stopped");

        // Export WAV and save to hidden input field
        rec.exportWAV(function (blob) {
            const reader = new FileReader();
            reader.onloadend = function () {
                // Save the Base64 result to the hidden input field
                document.getElementById(`id_audio_answer_${questionId}`).value = reader.result;
                console.log("Audio saved to form field");
            };
            reader.readAsDataURL(blob);
        });
    }
}
