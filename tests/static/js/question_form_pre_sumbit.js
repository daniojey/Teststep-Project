document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('question_form_id');
    const scoresSelect = document.getElementById('scoresFor');
    const numberInput = document.querySelector('.custom-number-input');
    const answerSelect = document.getElementById('answerSelect');
    console.log(form)

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        
        if (answerSelect.value === "AUD") {
            const scoresType = document.createElement('input');
            scoresType.type = 'hidden';
            scoresType.name = 'scores_for';
            scoresType.value = 'SQ'

            form.appendChild(scoresType);
        }

        if (scoresSelect.value === "SA") {
            numberInput.disabled = true;

            const newNumberInput = document.createElement('input');
            newNumberInput.type = 'hidden';
            newNumberInput.name = 'scores';
            newNumberInput.value = 0;

            form.appendChild(newNumberInput)
        }


        form.submit();
    })
});