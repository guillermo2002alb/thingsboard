# config.py

import os

# Carga las variables desde .env


# TTN (The Things Network)
TTN_APP_ID  = os.getenv("TTN_APP_ID")
TTN_API_KEY = os.getenv("TTN_API_KEY")
TTN_BROKER  = os.getenv("TTN_BROKER")
TTN_PORT    = int(os.getenv("TTN_PORT", 8883))

# ThingsBoard (REST)
TB_HOST = os.getenv("TB_HOST")      # p.ej. http://rt.ugr.es:8953
TB_TOKEN = os.getenv("TB_TOKEN")    # p.ej. 6iuio0kndkh7cwzb8wxm

# ThingsBoard (MQTT) – opcional
TB_MQTT_HOST  = os.getenv("TB_MQTT_HOST")
TB_MQTT_PORT  = int(os.getenv("TB_MQTT_PORT", 1885))
TB_MQTT_TOKEN = os.getenv("TB_MQTT_TOKEN")
