import socket
import json
import time

#    - "192.168.0.233"
#    - "192.168.0.105"
#    - "192.168.0.200"
#    - "192.168.0.59"
#    - "192.168.0.56"

IP = ["192.168.0.105", "192.168.0.200", "192.168.0.59", "192.168.0.56"]  # Cambia con l'IP della tua presa CozyLife
#IP = ["192.168.0.200"]  # Cambia con l'IP della tua presa CozyLife
PORT = 5555

def get_sn():
    return str(int(round(time.time() * 1000)))

def send_command(sock, command):
    payload = json.dumps(command) + "\r\n"
    sock.send(payload.encode('utf-8'))
    data = sock.recv(2048).decode('utf-8').strip().split("\n")[0]
    return json.loads(data)

# Connessione al dispositivo
for ip in IP:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(3)
        s.connect((ip, PORT))

        print(f"Connesso a {ip}:{PORT}")

    
        valid_attrs = {}

        for attr_id in range(0, 75):
            command = {
                'cmd': 2,
                'pv': 0,
                'sn': get_sn(),
                'msg': {
                    'attr': [attr_id]
                }
            }
            try:
                response = send_command(s, command)
                if response.get("res") == 0:
                    valid_attrs[attr_id] = response.get("msg", {}).get("data", {}).get(str(attr_id))
                   # print(f"Attr {attr_id}: {valid_attrs[attr_id]}")
            except Exception as e:
                print(f"Errore con attr {attr_id}: {e}")
    
        s.close()

        print(f"\n---{ip} Attributi validi trovati ---")
        for attr_id, value in valid_attrs.items():
            if value is not None:
                print(f"Attr {attr_id}: {value}")


#attributes found in CozyLife device:
#1 0 status on / off
#2 0    countdown timer missing seconds
#3: 00000000000000000000000000000000000000000000000000     timer management (max 5 timers, number of characters according to the number of timers)
# 4: 0
# 5: 0000000000
# 6: 2540363928
# 7: 0000000000
# 8: 0
# 9: 0000000000
# 10: 0
# 11: 0000000000
# 12: 0
# 13: 0000000000
# 14: 0
# 15: 0000000000
# 16: 2955664131
# 17: 0000000000
# 18: 2           configuration behaviour on power on 2 : restore last value, 1 all on , 0 all off
# 19: 1
# 26: 17          PROBABLY daily energy consumption in watt
# 27: 1700        Actual current mA
# 28: 1           Actual power W
# 29: 228         Actual voltage V
# 32: 1           Setting overcurrent protection
# 42: 17          PROBABLY total energy consumption in watt
# 52: 0
# 53: 0
# 54: 65536
# 55: 0
# 56: 65535
# 57: 255
# 58: 65535
# 59: 255
# 60: 65535
# 61: 255
# 62: 65535
# 63: 255
# 64: 65535
# 65: 255
# 66: 65535
# 67: 255
# 68: 0
# 69: 0
# 70: 0
# 71: 0
# 72: 5
# 73: 50
# 74: 0