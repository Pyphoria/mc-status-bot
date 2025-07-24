from mcstatus import JavaServer
import requests, time, os
from keep_alive import keep_alive

keep_alive()

# Umgebungsvariablen
server_ip = os.getenv("SERVER_IP")
webhook_url = os.getenv("WEBHOOK")
start_link = os.getenv("START_LINK")
bedrock_ip = os.getenv("BEDROCK_IP")        
bedrock_port = os.getenv("BEDROCK_PORT")
last_message = ""
CHECK_INTERVAL = 10

while True:
    try:
        server = JavaServer.lookup(server_ip)
        status = server.status()
        online = status.players.online
        max_players = status.players.max

        try:
            players = [p.name for p in status.players.sample]
        except:
            players = []

        fake_status = any("FalixNodes.net" in p or "OFFLINE" in p.upper() for p in players)

        if fake_status:
            raise Exception("Fake-Status erkannt")

        players_list = ", ".join(players) if players else "Niemand online"
        message = (
            "🟢 **Server ONLINE!**\n"
            f"👥 Spieler: {online}/{max_players}\n"
            f"🎮 Online: {players_list}\n\n"
            f"📡 **Java-IP:** `{server_ip}`\n"
            f"📱 **Bedrock-IP:** `{bedrock_ip}`\n"
            f"🔌 **Port:** `{bedrock_port}`"
        )
        payload = {"content": message}

    except:
        message = (
            "🔴 **Server ist offline oder nicht erreichbar.**\n"
            f"Du kannst ihn hier manuell starten:\n{start_link}\n\n"
            f"📡 **Java-IP:** `{server_ip}`\n"
            f"📱 **Bedrock-IP:** `{bedrock_ip}`\n"
            f"🔌 **Port:** `{bedrock_port}`"
        )
        payload = {"content": message}

    if message != last_message:
        requests.post(webhook_url, json=payload)
        last_message = message

    time.sleep(CHECK_INTERVAL)
