import os
import logging
import requests
import schedule
import time
from mcstatus import JavaServer
from keep_alive import keep_alive

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Webserver zum "wachhalten"
keep_alive()

# Umgebungsvariablen laden
server_ip = os.getenv("SERVER_IP")
webhook_url = os.getenv("WEBHOOK")
start_link = os.getenv("START_LINK")
bedrock_ip = os.getenv("BEDROCK_IP")
bedrock_port = os.getenv("BEDROCK_PORT")

# Variablen prüfen
required_vars = ["SERVER_IP", "WEBHOOK", "START_LINK", "BEDROCK_IP", "BEDROCK_PORT"]
for var in required_vars:
    if not os.getenv(var):
        raise RuntimeError(f"Umgebungsvariable {var} fehlt!")

# Letzte Nachricht merken
last_message = ""


def check_server():
    global last_message
    try:
        server = JavaServer.lookup(server_ip)
        status = server.status()

        online = status.players.online
        max_players = status.players.max

        try:
            players = [p.name for p in status.players.sample]
        except Exception:
            players = []

        fake_status = any("FalixNodes.net" in p or "OFFLINE" in p.upper() for p in players)
        if fake_status:
            raise Exception("Fake-Status erkannt")

        players_list = ", ".join(players) if players else "Niemand online"

        message = (
            f"🟢 Server ONLINE!\n"
            f"👥 Spieler: {online}/{max_players}\n"
            f"🎮 Online: {players_list}"
        )

        payload = {
            "embeds": [
                {
                    "title": "🟢 Server ONLINE!",
                    "fields": [
                        {"name": "Spieler", "value": f"{online}/{max_players}", "inline": True},
                        {"name": "Online", "value": players_list, "inline": False},
                        {"name": "Java-IP", "value": f"`{server_ip}`", "inline": True},
                        {"name": "Bedrock-IP", "value": f"`{bedrock_ip}`", "inline": True},
                        {"name": "Port", "value": f"`{bedrock_port}`", "inline": True},
                    ],
                    "color": 3066993,  # Grün
                }
            ]
        }

    except Exception as e:
        logging.warning(f"Server nicht erreichbar: {e}")
        message = "🔴 Server ist offline oder nicht erreichbar."
        payload = {
            "embeds": [
                {
                    "title": "🔴 Server OFFLINE",
                    "description": f"Du kannst ihn hier manuell starten:\n{start_link}",
                    "fields": [
                        {"name": "Java-IP", "value": f"`{server_ip}`", "inline": True},
                        {"name": "Bedrock-IP", "value": f"`{bedrock_ip}`", "inline": True},
                        {"name": "Port", "value": f"`{bedrock_port}`", "inline": True},
                    ],
                    "color": 15158332,  # Rot
                }
            ]
        }

    # Nur senden, wenn sich die Nachricht geändert hat
    if message != last_message:
        try:
            requests.post(webhook_url, json=payload, timeout=5)
            logging.info("Nachricht an Discord gesendet.")
            last_message = message
        except requests.exceptions.RequestException as e:
            logging.error(f"Fehler beim Senden an Discord: {e}")


# Scheduler: alle 10 Sekunden ausführen
schedule.every(10).seconds.do(check_server)

if __name__ == "__main__":
    logging.info("Bot gestartet.")
    while True:
        schedule.run_pending()
        time.sleep(1)
