document.addEventListener('DOMContentLoaded', () => {
    const answersScores = document.querySelectorAll('#answerScore');
    console.log(answersScores)

    const questionScores = document.querySelectorAll('#questionScore');

    if (questionScores.length !== 0) {
        questionScores.forEach(element => {
            console.log(element.value)
            element.value = parseFloat(element.value.replace(',', '.'))
        })
    }

    if (answersScores.length !== 0) {
        answersScores.forEach(element => {
            console.log(element.value)
            element.value = parseFloat(element.value.replace(',', '.'))
        })
    }
})

// function ZeroCutting(score) {
//     if (parseFloat(score.replace(',', '.'))) {
//         return parseFloat(score)
//     }
// }