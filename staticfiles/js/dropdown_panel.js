function toggleGroup(groupId) {
    var groupContent = document.getElementById(groupId);
    var arrow = groupContent.previousElementSibling.querySelector('.arrow'); // Находим стрелку в заголовке

    if (groupContent.style.display === "none" || groupContent.style.display === "") {
        groupContent.style.display = "block";
        arrow.classList.add("rotate"); // Поворачиваем стрелку
    } else {
        groupContent.style.display = "none";
        arrow.classList.remove("rotate"); // Возвращаем стрелку в исходное положение
    }
}