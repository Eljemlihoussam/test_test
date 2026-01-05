const API_URL = "/latest/";

async function refresh() {
  try {
    const res = await fetch(API_URL);
    const data = await res.json();

    document.getElementById("temp-value").textContent = data.temperature + " °C";
    document.getElementById("hum-value").textContent  = data.humidity + " %";

    const t = new Date(data.timestamp).toLocaleString();
    document.getElementById("temp-time").textContent = t;
    document.getElementById("hum-time").textContent  = t;
  } catch (e) {
    console.error(e);
  }
}

refresh();
setInterval(refresh, 20000);