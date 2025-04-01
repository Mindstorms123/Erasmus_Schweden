import json
import socket

class GreifarmClient:
    def __init__(self, server_ip, port=8005):
        self.server_ip = server_ip
        self.port = port

    def send_servo_positions(self, x=90, y=90, z=90):
        x = max(90, min(270, x))
        y = max(90, min(270, y))
        z = max(90, min(270, z))
        data = {"x": x, "y": y, "z": z}
        return self._send_request(data)

    def toggle_magnet(self, state):
        data = {"magnet": state}
        return self._send_request(data)

    def shutdown_server(self):
        data = {"shutdown": True}
        return self._send_request(data)

    def _send_request(self, data):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.server_ip, self.port))
                request = "POST / HTTP/1.1\r\n"
                request += "Content-Type: application/json\r\n"
                request += f"Content-Length: {len(json.dumps(data))}\r\n"
                request += "Connection: close\r\n\r\n"
                request += json.dumps(data)
                s.sendall(request.encode('utf-8'))
                response = s.recv(1024)
                return response.decode('utf-8')
        except Exception as e:
            return {"error": str(e)}

# Beispielnutzung
if __name__ == "__main__":
    client = GreifarmClient("192.168.1.100")  # Server-IP anpassen
    print(client.send_servo_positions(x=120, y=150, z=200))
    print(client.toggle_magnet(True))
    print(client.shutdown_server())
