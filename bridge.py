# bridge.py
# Script to bridge TTN uplinks to ThingsBoard vía MQTT individual por dispositivo

import json
import ssl
import time
import paho.mqtt.client as mqtt
from config import (
    TTN_APP_ID, TTN_API_KEY, TTN_BROKER, TTN_PORT,
    TB_MQTT_HOST, TB_MQTT_PORT
)

# MQTT topic para recibir todos los uplinks del app de TTN
TTN_TOPIC = f"v3/{TTN_APP_ID}@ttn/devices/+/up"

# Diccionario de tokens ThingsBoard por dispositivo TTN
TB_DEVICE_TOKENS = {
    "sensor-tutor": "9eXpPT5uJiXU9k9VQDyg",
    "sensor-sinco2": "WISrC52gabq8eC0S4Iln",
    "my-tfg-2025": "6iuio0kndkh7cwzb8wxm"
}

# -------------------------------------------------------------------
# 1) Callbacks de conexión y mensajes de TTN
# -------------------------------------------------------------------

def on_ttn_connect(client, userdata, flags, rc):
    print(f"[TTN] Conectado con código {rc}")
    client.subscribe(TTN_TOPIC)
    print(f"[TTN] Subscrito a {TTN_TOPIC}")

def on_ttn_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        device_id = payload["end_device_ids"]["device_id"]
        decoded_container = payload["uplink_message"]["decoded_payload"]
        if isinstance(decoded_container, dict) and "data" in decoded_container:
            decoded = decoded_container["data"]
        else:
            decoded = decoded_container
        timestamp = payload["uplink_message"]["received_at"]
    except Exception as e:
        print(f"[TTN] Error al parsear payload: {e}")
        return

    tb_values = decoded.copy()
    tb_values["ts"] = timestamp

    publish_to_tb_mqtt(device_id, tb_values)

# -------------------------------------------------------------------
# 2) Publicar en ThingsBoard MQTT por token individual
# -------------------------------------------------------------------

def publish_to_tb_mqtt(device_id, values):
    token = TB_DEVICE_TOKENS.get(device_id)
    if token is None:
        print(f"[TB-MQTT] {device_id} no tiene token asignado. Ignorado.")
        return

    client = mqtt.Client(client_id=f"tb_{device_id}")
    client.username_pw_set(token)
    try:
        client.connect(TB_MQTT_HOST, TB_MQTT_PORT)
        client.loop_start()
        topic = "v1/devices/me/telemetry"
        payload = json.dumps(values)
        result = client.publish(topic, payload)
        status = result[0]
        if status == 0:
            print(f"[TB-MQTT] {device_id} publicado correctamente")
        else:
            print(f"[TB-MQTT] Error publicando en {device_id}: {status}")
        time.sleep(0.5)
    except Exception as e:
        print(f"[TB-MQTT] Error en {device_id}: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

# -------------------------------------------------------------------
# 3) Main: conectar a TTN
# -------------------------------------------------------------------

def main():
    ttn_client = mqtt.Client()
    ttn_client.username_pw_set(f"{TTN_APP_ID}@ttn", TTN_API_KEY)
    ttn_client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    ttn_client.tls_insecure_set(False)
    ttn_client.on_connect = on_ttn_connect
    ttn_client.on_message = on_ttn_message

    print("[TTN] Conectando…")
    ttn_client.connect(TTN_BROKER, TTN_PORT)
    ttn_client.loop_start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[TTN] Deteniendo puente…")
    finally:
        ttn_client.loop_stop()

if __name__ == "__main__":
    main()
