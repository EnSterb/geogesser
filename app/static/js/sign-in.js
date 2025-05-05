document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login-form");
  const errorMessage = document.getElementById("error-message");

  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = form.email.value;
    const password = form.password.value;

    const data = { username: email, password }; // Для OAuth2PasswordRequestForm username - это email

    try {
      const response = await fetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded" // Используем form-urlencoded
        },
        body: new URLSearchParams(data).toString(), // Переход от JSON к form-urlencoded
      });

      if (response.ok) {
        window.location.href = "/pages/hub"; // Редирект на главную страницу или dashboard
      } else {
        const errorData = await response.json();
        let message = errorData.detail || "Ошибка при входе";
        if (message.startsWith("400: ")) {
          message = message.substring(5); // Убираем первые 5 символов, если они есть
        }
        errorMessage.textContent = message; // Показываем ошибку в div
        errorMessage.style.display = "block"; // Делаем ошибку видимой
      }
    } catch (error) {
      errorMessage.textContent = "Ошибка при регистрации: " + error.message;
      errorMessage.style.display = "block"; // Показываем ошибку в div
    }
  });
});
