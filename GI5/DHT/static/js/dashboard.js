const API_URL = "/latest/";
const POST_URL = "/api/post/";

// Fonction pour récupérer le cookie CSRF
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function formatValue(value, suffix) {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return "--";
  }
  return `${Number(value).toFixed(1)} ${suffix}`.trim();
}

function computeRole(temp) {
  // 3 rôles selon la température : <2 (role 3), 2-20 (role 1), >20 (role 2)
  if (temp === undefined || temp === null || Number.isNaN(temp)) {
    return { label: "Inconnu", detail: "Aucune mesure" };
  }
  if (temp < 2) {
    return { label: "Rôle 3 (Alerte basse)", detail: "Température < 2°C" };
  }
  if (temp > 20) {
    return { label: "Rôle 2 (Alerte haute)", detail: "Température > 20°C" };
  }
  return { label: "Rôle 1 (Normal)", detail: "Température normale (2°C - 20°C)" };
}

async function refreshDashboard() {
  try {
    const response = await fetch(API_URL, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const timestamp = data.timestamp ? new Date(data.timestamp).toLocaleString() : "--";

    document.getElementById("temp-value").textContent = formatValue(data.temperature, "°C");
    document.getElementById("hum-value").textContent = formatValue(data.humidity, "%");

    document.getElementById("temp-time").textContent = timestamp;
    document.getElementById("hum-time").textContent = timestamp;

    const role = computeRole(data.temperature);
    document.getElementById("incident-status").textContent = role.label;
    document.getElementById("incident-detail").textContent = role.detail;
  } catch (error) {
    console.error("Dashboard refresh error:", error);
    document.getElementById("temp-value").textContent = "--";
    document.getElementById("hum-value").textContent = "--";
    document.getElementById("temp-time").textContent = "Erreur de chargement";
    document.getElementById("hum-time").textContent = "Erreur de chargement";
    document.getElementById("incident-status").textContent = "Inconnu";
    document.getElementById("incident-detail").textContent = "Impossible de charger les données";
  }
}

function bindManualForm() {
  const form = document.getElementById("manual-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const temp = parseFloat(document.getElementById("manual-temp").value);
    const hum = parseFloat(document.getElementById("manual-hum").value);
    const resultEl = document.getElementById("manual-result");

    resultEl.textContent = "Envoi...";
    try {
      // Récupérer le token CSRF (depuis la variable globale ou le cookie)
      const csrftoken = typeof CSRF_TOKEN !== 'undefined' && CSRF_TOKEN !== '' 
        ? CSRF_TOKEN 
        : (getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value);
      
      console.log('CSRF Token:', csrftoken ? 'Found' : 'Not found');
      
      const headers = { 
        "Content-Type": "application/json",
      };
      
      // Ajouter le token CSRF si disponible
      if (csrftoken && csrftoken !== 'NOTPROVIDED') {
        headers["X-CSRFToken"] = csrftoken;
      }
      
      const res = await fetch(POST_URL, {
        method: "POST",
        headers: headers,
        body: JSON.stringify({ temp, hum })
      });
      const payload = await res.json();
      if (!res.ok) {
        throw new Error(payload?.detail || res.statusText);
      }
      resultEl.textContent = "Mesure envoyée avec succès.";
      refreshDashboard();
    } catch (err) {
      console.error(err);
      resultEl.textContent = "Erreur: " + err.message;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  refreshDashboard();
  setInterval(refreshDashboard, 20000);
  bindManualForm();
});

