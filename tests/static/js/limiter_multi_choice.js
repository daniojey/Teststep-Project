document.addEventListener('DOMContentLoaded', () => {
    // Скрипт для ограничения количества выбираемых чекбоксов для ответов типа MC(MULTIPLE_CHOICE)

    const form = document.querySelector('.form-group');
    const answers_count = form.dataset.answersCount

    if (answers_count) {

        let checkBoxCount = 0;
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');

        checkboxes.forEach(box => {
            // console.log(box)

            box.addEventListener('change', (e) => {
                    if (box.checked === true) {

                        if (checkBoxCount >= answers_count) {
                            box.checked = false

                        } else {

                            checkBoxCount += 1
                            // console.log(checkBoxCount)

                            if (checkBoxCount >= answers_count) {
                                const unselectedCheckBoxes = Array.from(checkboxes).filter(checkbox => checkbox.checked === false);
                                // console.log(unselectedCheckBoxes)

                                unselectedCheckBoxes.forEach(checkbox => {
                                    // console.log(checkbox.id)
                                    const parts = checkbox.id.split('_');
                                    const lastString = parts[parts.length - 1]

                                    if (lastString) {
                                        const checkboxLabel = document.querySelector(`.mc-${lastString}`)
                                        // console.log(checkboxLabel)
                                        checkboxLabel.classList.add('lock-checkbox')
                                    }
                                    // console.log(lastString)
                                });
                            }
                        }

                    } else {

                        checkBoxCount -= 1
                        // console.log(checkBoxCount)
                        
                        const allCheckboxes = document.querySelectorAll('.custom-checkbox-box');

                        allCheckboxes.forEach(checkbox => {
                            if (checkbox.classList.contains('lock-checkbox')) {
                                checkbox.classList.remove('lock-checkbox');
                            }
                        })
                    }
        
            })
        })
    }
})