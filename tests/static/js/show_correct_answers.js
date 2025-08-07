

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('test-form');
    const questionAnswerType = form.dataset.currentQuestion;
    const questionType = form.dataset.questionType;
    const dataAnswers = form.dataset.answers;
    console.log(questionType)

    if (questionType === "MTCH") {
        const leftItems = document.querySelectorAll('.left-item')
        const parsedData = JSON.parse(dataAnswers);
        console.log(parsedData);
        console.log(leftItems);

        leftItems.forEach(element => {
            const rightElement = element.querySelector('.right-item')
            const elementData = element.dataset.leftItem
            const rightData = rightElement.dataset.rightItem
            // console.log(elementData)
            // console.log(rightData)
            // console.log(dataAnswers)
            // console.log(parsedData[elementData])
            if (parsedData[elementData] == String(rightData)) {
                console.log(element)
                element.style.borderColor = "#7eff42";
                
                console.log(parsedData[elementData], '==', rightData);
            } else {
                element.style.borderColor = "#ff7c7c";
            }
        })

    } else if (questionAnswerType === 'SC' | questionAnswerType === "MC") {
        const parsedData = JSON.parse(dataAnswers);
        console.log(parsedData);

        for (const element in parsedData) {
            console.log(element)
            console.log(parsedData[element])
            const valueElement = document.querySelector(`[value="${element}"]`);
            const parrentElement = valueElement.parentElement
            parrentElement.style.color = "#7eff42";

        };
    } else if (questionAnswerType == "INP") {
        const parsedData = JSON.parse(dataAnswers);
        console.log(parsedData);
        const popupWindow = document.querySelector('.popup-window');
        const questionText = document.querySelector('.text-question')

        let timers = new Map()

        for (const element in parsedData) {
            const newElement = document.createElement('p');

            newElement.textContent = parsedData[element]

            popupWindow.appendChild(newElement)
        }

        questionText.addEventListener('mousemove', (e) => {
            clearTimeout(timers.get('timer'))
            popupWindow.style.left = e.pageX + 10 + "px";
            popupWindow.style.top = e.pageY + 10 + "px";
            popupWindow.style.animation = "fadeIn 0.3s ease";
            popupWindow.style.animationFillMode = "forwards";
            popupWindow.style.display = 'flex';
        })

        questionText.addEventListener('mouseout', () => {
            popupWindow.style.animation = "hideIn 0.3s ease";
            popupWindow.style.animationFillMode = "forwards";

            let timerId = setTimeout(() => {
                popupWindow.style.display = 'none';
            }, 300)

            timers.set('timer', timerId)
        })
    }
    


})