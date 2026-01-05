# Configuration Arduino ESP8266 pour DHT11

## Problèmes résolus

### 1. Erreur CSRF (403 Forbidden)
✅ **Résolu** : L'API `/api/post/` est maintenant publique et ne nécessite plus de token CSRF.

### 2. Timeout avec PythonAnywhere
Le timeout peut être dû à plusieurs raisons :
- Le serveur PythonAnywhere peut être en veille
- Le certificat SSL peut poser problème
- Le timeout réseau de l'ESP8266 est trop court

## Configuration pour serveur local

Si vous testez en local, modifiez l'URL dans le code Arduino :

```cpp
// Pour serveur local (remplacez par votre IP locale)
const char* SERVER_URL = "http://192.168.1.XXX:8000/api/post/";
```

**Important** : 
- Utilisez `http://` (pas `https://`) pour le serveur local
- Remplacez `192.168.1.XXX` par l'IP de votre ordinateur
- Assurez-vous que le serveur Django tourne : `python manage.py runserver 0.0.0.0:8000`

## Configuration pour PythonAnywhere

### Code Arduino modifié (avec timeout augmenté)

```cpp
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <DHT.h>
#include <ArduinoJson.h>

// Configuration WiFi
const char* WIFI_SSID = "Hou Ssam";
const char* WIFI_PASSWORD = "Houssam123@.";

// Capteur DHT11
#define DHTPIN D4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// API Django (HTTPS/pythonanywhere)
const char* SERVER_URL = "https://houssamyasser.pythonanywhere.com/api/post/";

// Intervalle d'envoi (20 min)
const unsigned long INTERVAL = 1200000; // 20 minutes
unsigned long previousMillis = 0;

void connectWiFi();
void envoyerDonnees();

void setup() {
  Serial.begin(9600);
  delay(1000);
  Serial.println();
  Serial.println("=== Cold Chain Monitoring - ESP8266 ===");
  dht.begin();
  Serial.println("✅ DHT11 initialisé");
  connectWiFi();
  envoyerDonnees();
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= INTERVAL) {
    previousMillis = currentMillis;
    envoyerDonnees();
  }
  delay(1000);
}

void connectWiFi() {
  Serial.print("🔌 Connexion WiFi : ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ WiFi connecté !");
    Serial.print("📶 IP : ");
    Serial.println(WiFi.localIP());
    Serial.print("📡 RSSI : ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\n❌ Échec connexion WiFi");
  }
}

void envoyerDonnees() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi déconnecté, reconnexion...");
    connectWiFi();
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("❌ Impossible d'envoyer (WiFi KO)");
      return;
    }
  }

  float temperature = dht.readTemperature();
  float humidite = dht.readHumidity();

  if (isnan(temperature) || isnan(humidite)) {
    Serial.println("❌ Lecture DHT11 invalide");
    return;
  }

  Serial.println("\n--- 📊 Nouvelle mesure ---");
  Serial.printf("🌡️  Température : %.2f °C\n", temperature);
  Serial.printf("💧 Humidité : %.2f %%\n", humidite);

  StaticJsonDocument<200> doc;
  doc["temp"] = temperature;
  doc["hum"] = humidite;
  String jsonString;
  serializeJson(doc, jsonString);
  Serial.print("📦 JSON : ");
  Serial.println(jsonString);

  // HTTPS avec timeout augmenté
  WiFiClientSecure client;
  client.setInsecure();  // Accepte le certificat HTTPS automatiquement
  client.setTimeout(15000);  // Timeout de 15 secondes (augmenté)
  
  HTTPClient http;
  http.begin(client, SERVER_URL);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(15000);  // Timeout HTTP de 15 secondes
  
  Serial.print("🚀 Envoi vers : ");
  Serial.println(SERVER_URL);

  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) {
    Serial.print("✅ HTTP : ");
    Serial.println(httpResponseCode);
    Serial.print("📥 Réponse serveur : ");
    Serial.println(http.getString());
    
    // Vérifier si un incident a été créé
    if (httpResponseCode == 201) {
      Serial.println("✅ Données enregistrées avec succès !");
    }
  } else {
    Serial.print("❌ Erreur HTTP : ");
    Serial.println(http.errorToString(httpResponseCode).c_str());
    Serial.println("💡 Vérifiez que le serveur est accessible et en ligne");
  }

  http.end();
  Serial.println("----------------------------\n");
}
```

## Modifications importantes

1. **Timeout augmenté** : `client.setTimeout(15000)` et `http.setTimeout(15000)` (15 secondes)
2. **Pas de CSRF** : L'API est maintenant publique, pas besoin de token
3. **Gestion d'erreurs améliorée** : Messages plus clairs

## Vérification PythonAnywhere

1. **Vérifiez que le serveur est en ligne** :
   - Allez sur https://houssamyasser.pythonanywhere.com/
   - Vérifiez que le site répond

2. **Vérifiez l'API** :
   - Testez : `curl https://houssamyasser.pythonanywhere.com/api/post/ -X POST -H "Content-Type: application/json" -d '{"temp":10.4,"hum":82.4}'`

3. **Vérifiez les logs** :
   - Dans PythonAnywhere, allez dans "Tasks" ou "Web" pour voir les logs
   - Vérifiez s'il y a des erreurs

## Test local

Pour tester en local d'abord :

1. Trouvez votre IP locale :
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   ```

2. Modifiez l'URL dans Arduino :
   ```cpp
   const char* SERVER_URL = "http://192.168.1.XXX:8000/api/post/";
   ```

3. Lancez Django avec :
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

4. Testez depuis l'Arduino

## Dépannage

### Timeout persistant
- Vérifiez que le serveur PythonAnywhere n'est pas en veille
- Augmentez encore le timeout (20-30 secondes)
- Vérifiez la connexion WiFi de l'ESP8266

### Erreur 403
- ✅ Résolu : L'API est maintenant publique

### Erreur de connexion
- Vérifiez que l'ESP8266 est connecté au WiFi
- Vérifiez que l'URL est correcte
- Testez avec un navigateur d'abord

