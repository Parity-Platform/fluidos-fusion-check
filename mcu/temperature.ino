#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Broker settings
const char* mqtt_broker = "YOUR_KUBEDGE_BROKER_ADDRESS";
const int mqtt_port = 1883;
const char* mqtt_username = "YOUR_MQTT_USERNAME";
const char* mqtt_password = "YOUR_MQTT_PASSWORD";
const char* client_id = "esp32_client";

// DHT sensor settings
#define DHTPIN 4       // DHT sensor pin
#define DHTTYPE DHT22  // DHT22 (AM2302) sensor type
DHT dht(DHTPIN, DHTTYPE);

// MQTT topics
const char* temp_topic = "sensors/temperature";
const char* humidity_topic = "sensors/humidity";

// Initialize WiFi and MQTT client
WiFiClient espClient;
PubSubClient client(espClient);

// Timing variables
unsigned long lastMsg = 0;
const long interval = 30000;  // Publish every 30 seconds

void setup_wifi() {
  delay(10);
  Serial.println("Connecting to WiFi...");
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect(client_id, mqtt_username, mqtt_password)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Setup WiFi
  setup_wifi();
  
  // Configure MQTT broker
  client.setServer(mqtt_broker, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > interval) {
    lastMsg = now;
    
    // Read sensor values
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    
    // Check if readings are valid
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("Failed to read from DHT sensor!");
      return;
    }
    
    // Convert values to strings
    char temp_str[8];
    char humidity_str[8];
    dtostrf(temperature, 6, 2, temp_str);
    dtostrf(humidity, 6, 2, humidity_str);
    
    // Publish to MQTT broker
    client.publish(temp_topic, temp_str);
    client.publish(humidity_topic, humidity_str);
    
    // Print values to Serial for debugging
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print("°C, Humidity: ");
    Serial.print(humidity);
    Serial.println("%");
  }
}