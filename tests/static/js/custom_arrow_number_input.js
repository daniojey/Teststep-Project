// JavaScript для функциональности стрелок
document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.arrow.up').addEventListener('click', (e) => {
        e.preventDefault();
        const input = document.querySelector('.number-input');
        input.stepUp();
    });
    
    document.querySelector('.arrow.down').addEventListener('click', (e) => {
        e.preventDefault();
        const input = document.querySelector('.number-input');
        if (input.value > 0) {
            input.stepDown();
        }
    });
});