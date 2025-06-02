// JavaScript для функциональности стрелок
document.addEventListener('DOMContentLoaded', () => {
    const scoresSelect = document.getElementById('scoresFor');
    const numberInput = document.querySelector('.custom-number-input');
    const answerSelect = document.getElementById('answerSelect');

    if (answerSelect) {
        answerSelect.addEventListener('change', () => {
            if (answerSelect.value == "AUD") {
                scoresSelect.value = "SQ";
                scoresSelect.disabled = true;
                numberInput.style.display = 'flex';
                numberInput.required = true;
            } else {

                if (answerSelect.value !== "AUD") {
                    scoresSelect.disabled = false;
                    numberInput.required = false;
                }
            }
        })
    }

    if (scoresSelect) {
        scoresSelect.addEventListener('change', (e) => {
        console.log(e.target.value);

        if (e.target.value === "SQ") {
            numberInput.style.display = 'flex';
        } else {
            numberInput.style.display = 'none';

            // numberInput.blur();
            // numberInput.value = "";
            // numberInput.removeAttribute('value');
            // const event = new Event('input', { bubbles: true });
            // numberInput.dispatchEvent(event);

            // console.log('numberInput', numberInput.value)
        }
        });
    };
   

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