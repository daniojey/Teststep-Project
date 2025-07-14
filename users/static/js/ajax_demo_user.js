document.addEventListener("DOMContentLoaded", () => {
    const createDemoBtn = document.getElementById('createDemoBtn');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value

    createDemoBtn.addEventListener('click', async (e) => {
        e.preventDefault();

        const response = await fetch('/user/create_demo/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })

            .then(response => {
                if (response.ok) {
                    return response.json()
                } else {
                    throw Error('Помилка обробки')
                }
            })
            .then(data => {
                showMessage(action = "success", message = data.message);
                setTimeout(() => window.location.href = "/", 1000);
            })
            .catch(error => {
                showMessage(action = "error", message = error);
            })
    })

})


async function showMessage(action, message) {
    const notification = document.createElement("div");
    notification.className = "error-notification";
    notification.textContent = message;

    if (action == 'error') {
        notification.classList.add("error");
    } else if (action === 'success') {
        notification.classList.add("success");
        // setTimeout(() => window.location.href = "/", 1000);
    }

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add("hide");
    }, 4000);

    setTimeout(() => {
        notification.remove();
    }, 4500);


}