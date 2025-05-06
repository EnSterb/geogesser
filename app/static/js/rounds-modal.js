document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("create-room-modal");
  const openBtn = document.getElementById("create-game-btn"); // ← Исправлено имя ID
  const closeBtn = document.getElementById("close-modal-btn");
  const form = document.getElementById("create-room-form");

  if (!modal || !openBtn || !closeBtn || !form) {
    console.error("Не найден один из элементов формы.");
    return;
  }

  openBtn.addEventListener("click", () => {
    modal.style.display = "flex";
  });

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const rounds = form.rounds.value;

    try {
      const res = await fetch("/game/create-solo-room", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rounds: Number(rounds) })
      });

      if (res.ok) {
        const data = await res.json();
        window.location.href = `/pages/single-room/${data.room_id}`;
      } else {
        alert("Ошибка при создании комнаты");
      }
    } catch (err) {
      console.error(err);
      alert("Ошибка соединения");
    }
  });
});
