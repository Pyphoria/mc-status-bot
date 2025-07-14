from mcstatus import JavaServer
import requests, time, os
from keep_alive import keep_alive

keep_alive()

server_ip = os.getenv("SERVER_IP")
webhook_url = os.getenv("WEBHOOK")

last_message = ""
CHECK_INTERVAL = 10  # Sekunden

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
        message = f"🟢 **Server ONLINE!**\n👥 Spieler: {online}/{max_players}\n🎮 Online: {players_list}"
        payload = {"content": message}

    except:
        message = (
            "🔴 **Server ist offline oder nicht erreichbar.**\n"
            "Du kannst ihn hier manuell starten:\n"
            "https://falixnodes.net/startserver?ip=tblockmcserver"
        )
        payload = {"content": message}

    if message != last_message:
        requests.post(webhook_url, json=payload)
        last_message = message

    time.sleep(CHECK_INTERVAL)
