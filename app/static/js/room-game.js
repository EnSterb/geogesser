const container = document.getElementById('mly');

const imageId = container.dataset.imageId;
const lat = parseFloat(container.dataset.lat);
const lng = parseFloat(container.dataset.lng);
// console.log(imageId)
// console.log(lat)
// console.log(lng)

var {Viewer} = mapillary;
// Mapillary Viewer
    const viewer = new Viewer({
        accessToken: 'MLY|9331669426931121|871cc49d836ea4351fc78506d6ab68cf',
        container: 'mly',
        imageId: imageId,
    });

// Leaflet Mini Map
    const map = L.map('map').setView([51.505, -0.09], 13);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const marker = L.marker([51.505, -0.09]).addTo(map);

    map.on('click', function (e) {
        marker.setLatLng([e.latlng.lat % 360, e.latlng.lng %360 ]);
        // console.log(e.latlng)
    });

const pathParts = window.location.pathname.split('/');
const ROOM_ID = parseInt(pathParts[pathParts.length - 1]);

// console.log({
//   room_id: ROOM_ID,
//   guessed_lat: marker.getLatLng().lat,
//   guessed_lng: marker.getLatLng().lng
// });

document.querySelector("#end-round-btn").addEventListener("click", function() {

  fetch("/game/single-game/end-round", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      room_id: ROOM_ID,
      guessed_lat: marker.getLatLng().lat % 360,
      guessed_lng: marker.getLatLng().lng % 360
    })
  })
  .then(res => res.json())
  .then(data => {
    // Увеличить карту
    document.querySelector("#map").style.width = "80%";
    document.querySelector("#map").style.height = "80%";

    // Удалить кнопку подтверждения
    document.querySelector("#end-round-btn")?.remove();
    // Использование стандартной иконки с изменённым цветом
        const redIcon = L.divIcon({
          className: 'leaflet-div-icon',
          html: '<div style="background-color: red; width: 20px; height: 20px; border-radius: 50%;"></div>',
          iconSize: [20, 20],  // Размер
          iconAnchor: [10, 10],  // Точка привязки
          popupAnchor: [0, -10]  // Точка всплывающего окна
        });


    // Добавить линию от ответа игрока до правильного места
    const correctLatLng = L.latLng(lat, lng);
    L.marker(correctLatLng, {icon: redIcon}).addTo(map);
    L.polyline([marker.getLatLng(), correctLatLng], {color: "blue"}).addTo(map);

// Удалить старый контейнер если он есть
let oldControls = document.querySelector("#game-controls");
if (oldControls) oldControls.remove();

// Создать контейнер
const controls = document.createElement("div");
controls.id = "game-controls";

// Блок с очками за раунд
const scoreBox = document.createElement("div");
scoreBox.innerText = `Вы получили ${data.score} очков`;
scoreBox.classList.add("score-box");
controls.appendChild(scoreBox);

if (data.left_rounds === 0) {
  // Если это был последний раунд — общий счёт
  const totalScoreBox = document.createElement("div");
  totalScoreBox.innerText = `Ваш итоговый счёт: ${data.total_score} очков`;
  totalScoreBox.classList.add("score-box");
  controls.appendChild(totalScoreBox);

  // Кнопка завершить
  const nextBtn = document.createElement("button");
  nextBtn.innerText = "Завершить игру";
  nextBtn.classList.add("action-button");
  nextBtn.onclick = () => window.location.href = "/pages/single-game";
  controls.appendChild(nextBtn);
} else {
  // Кнопка "Следующий раунд"
  const nextBtn = document.createElement("button");
  nextBtn.innerText = "Следующий раунд";
  nextBtn.classList.add("action-button");
  nextBtn.onclick = () => window.location.reload();
  controls.appendChild(nextBtn);
}

document.body.appendChild(controls);

  })
  .catch(error => {
    console.error("Ошибка при завершении раунда:", error);
  });
});