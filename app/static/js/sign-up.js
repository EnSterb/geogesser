document.querySelector(".auth-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const nickname = e.target.nickname.value;
    const email = e.target.email.value;
    const password = e.target.password.value;

    const errorMessageDiv = document.getElementById("error-message");
    errorMessageDiv.style.display = "none";
    errorMessageDiv.textContent = "";

    const data = { nickname, email, password };

    try {
        const response = await fetch("/auth/register/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            window.location.href = "/pages/email-sent";
        } else {
            const errorData = await response.json();

            let message = errorData.detail;
            if (typeof message === "string" && message.length > 5) {
              message = message.substring(5);
            }

            errorMessageDiv.textContent = message;
            errorMessageDiv.style.display = "block";
        }
    } catch (error) {
        errorMessageDiv.textContent = "Ошибка при отправке запроса: " + error.message;
        errorMessageDiv.style.display = "block";
    }
});
