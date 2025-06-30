document.addEventListener('DOMContentLoaded', () => {
    const groupHeaders = document.querySelectorAll('.group-header');

    groupHeaders.forEach(element => {
        element.addEventListener('click', () => {
            const groupContent = document.getElementById(`group_${element.dataset.groupid}`)
            const arrow = document.getElementById(`arrow_${element.dataset.groupid}`)

            if (groupContent.classList.contains('active')) {
                groupContent.style.height = "0";
                groupContent.classList.remove('active');
                arrow.classList.remove('rotate')
            } else {
                groupContent.style.height = groupContent.scrollHeight + 24 + 'px';
                groupContent.classList.add('active');
                arrow.classList.add('rotate')
            }
        });
    })
})