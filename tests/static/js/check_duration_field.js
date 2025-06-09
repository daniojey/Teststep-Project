document.addEventListener('DOMContentLoaded', () => {
    const durationField = document.getElementById('durationField');
    const testForm = document.getElementById('testForm');
    const saveBtn = document.querySelector('.save-btn');

    durationField.addEventListener('change', () => {
        const duration = parseInt(durationField.value, 10)
        
        if (duration && duration < 1440) {
            saveBtn.disabled = false;
        } else {
            saveBtn.disabled = true;
        }
    })

    // testForm.addEventListener('submit', (e) => {
    //     e.preventDefault()

    //     const duration = parseInt(durationField.value, 10)

    //     if (duration) {
    //         testForm.submit();
    //     }
    // })
})