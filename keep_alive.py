from flask import Flask
from threading import Thread

app = Flask('keep_alive')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8081)  # Different port

def keep_alive():
    t = Thread(target=run)
    t.start()
