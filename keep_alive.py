from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Ich bin wach! 🟢"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.start()
