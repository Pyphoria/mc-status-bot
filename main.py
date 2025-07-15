from mcstatus import JavaServer
import requests, time, os
from keep_alive import keep_alive

# Webserver starten, damit UptimeRobot den Bot wachhält
keep_alive()

# ENV-VARIABLEN laden
server_ip = os.getenv("SERVER_IP")        # z. B. t-block.falix.gg
webhook_url = os.getenv("WEBHOOK")        # Discord Webhook URL
start_link = os.getenv("START_LINK")      # z. B. https://panel.falixnodes.net/server/xyz/start
bedrock_port = os.getenv("BEDROCK_PORT")  # z. B. 31703

last_message = ""
CHECK_INTERVAL = 10  # alle 10 Sekunden prüfen

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

        # Fake-Status verhindern (wenn der Server noch gar nicht läuft)
        fake_status = any("FalixNodes.net" in p or "OFFLINE" in p.upper() for p in players)

        if fake_status:
            raise Exception("Fake-Status erkannt")

        players_list = ", ".join(players) if players else "Niemand online"
        message = (
            f"🟢 **Server ONLINE!**\n"
            f"👥 Spieler: {online}/{max_players}\n"
            f"🎮 Online: {players_list}\n"
            f"📱 Bedrock-Port: `{bedrock_port}`"
        )
        payload = {"content": message}

    except:
        message = (
            "🔴 **Server ist offline oder nicht erreichbar.**\n"
            f"Du kannst ihn hier manuell starten:\n{start_link}\n"
            f"📱 Bedrock-Port (für Handy & Konsole): `{bedrock_port}`"
        )
        payload = {"content": message}

    if message != last_message:
        requests.post(webhook_url, json=payload)
        last_message = message

    time.sleep(CHECK_INTERVAL)
