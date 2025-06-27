function toggleGroup(groupId) {
    const groupContent = document.getElementById(`group_${groupId}`);
    const arrow = document.getElementById(`arrow_${groupId}`);

    if (!groupContent.classList.contains('active')) {
        // groupContent.style.display = "block";
        groupContent.classList.add('active')
        groupContent.style.height = groupContent.scrollHeight + 'px'
        arrow.classList.add("rotate"); // Поворачиваем стрелку
    } else {
        // groupContent.style.display = "none";
        groupContent.classList.remove('active')
        groupContent.style.height = "0"
        arrow.classList.remove("rotate"); // Возвращаем стрелку в исходное положение
    };
}