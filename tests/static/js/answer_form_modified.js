document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('addQuestionForm');
    const scoresFor = document.getElementById('questionData');


    form.addEventListener("submit", (e) => {
        e.preventDefault();

        if (scoresFor.dataset.question === "SQ") {
            const scoreElem = document.createElement('input');
            scoreElem.type = 'hidden';
            scoreElem.name = 'score';
            scoreElem.value = 0;

            form.appendChild(scoreElem);
        }

        form.submit();
    })
})