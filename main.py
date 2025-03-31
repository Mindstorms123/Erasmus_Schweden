import network
import rp2
import utime as time
import socket
import json
from machine import I2C, Pin, ADC
from pca9685 import PCA9685
from servo import Servos
import ssd1306
import time

# Display wating time
pause = 4 # in sekounds


# Wifi data
ssid = #include wifi ssid here like 'wifiname'
wlPw = #include wifi password here like 'password'
rp2.country('DE')
PORT = 8005

# initialize servo and i2c
sda = Pin(0)
scl = Pin(1)
i2c_id = 0
i2c = I2C(id=i2c_id, sda=sda, scl=scl)
pca = PCA9685(i2c=i2c)
servo = Servos(i2c=i2c)

# initialize display
print('OLED-Display initialisieren')
oled_width = 128 # with: Pixel
oled_height = 64 # hight: Pixel
display = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
time.sleep(0.1)

# Display test
#print('Text zeilenweise darstellen')
#display.text('Hallo World 1', 0, 0) # Text, X, Y
#display.text('Hallo World 2', 0, 10)
#display.text('Hallo World 3', 0, 20)
#display.text('Hallo World 4', 0, 30)
#display.text('Hallo World 5', 0, 40)
#display.text('Hallo World 6', 0, 50)
#display.text('Hallo World 7', 0, 60)
#display.show()

#time.sleep(pause)

# delete Display 
print('Display deleted')
display.fill(0)
display.show()


# initialize electro magnet
magnet_pin = Pin(15, Pin.OUT)
magnet_state = False

# Flag to control the server loop
server_running = True

# connect to wifi
def wlanConnectundServer():
    global server_running, magnet_state
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, wlPw)
    print('Verbindung wird hergestellt...')
    while not wlan.isconnected():
        time.sleep(1)
    print('WLAN verbunden!')
    netConfig = wlan.ifconfig()
    HOST = netConfig[0]

    # HTTP-Server
    addr = socket.getaddrinfo(HOST, PORT)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    print('Server läuft auf', addr)
    display.text('Server IP:', 0, 0)
    display.text(HOST, 0, 10)
    display.text('Port:', 0, 20)
    display.text(str(PORT), 40, 20)
    display.show()
    led = Pin("LED", Pin.OUT)
    led.value(1)  # LED on

    try:
        while server_running:
            cl, addr = s.accept()
            print('Client verbunden von', addr)
            request = cl.recv(1024).decode('utf-8')
            
            if "POST" in request:
                headers, body = request.split("\r\n\r\n", 1)
                data = json.loads(body)
                if data.get("shutdown"):
                    server_running = False
                    print('Display löschen')
                    display.fill(0)
                    display.show()
                    response_data = json.dumps({"message": "Server wird heruntergefahren"})
                elif data.get("magnet") is not None:
                    magnet_state = data["magnet"]
                    magnet_pin.value(magnet_state)
                    print(f"Magnet {'aktiviert' if magnet_state else 'deaktiviert'}")
                    response_data = json.dumps({"message": "Magnet " + ("aktiviert" if magnet_state else "deaktiviert"), "magnet": magnet_state})
                else:
                    x_angle = int(data.get("x", 90))
                    y_angle = int(data.get("y", 90))
                    z_angle = int(data.get("z", 90))
                    
                    # Print the received data and servo positions to the console
                    print(f"Received data: {data}")
                    print(f"Setting servo positions to x: {x_angle}, y: {y_angle}, z: {z_angle}")
                    
                    # Move the servos to the specified angles
                    servo.position(index=0, degrees=max(90, min(270, x_angle)))
                    
                    servo.position(index=1, degrees=max(90, min(270, y_angle)))
                    servo.position(index=2, degrees=max(90, min(270, z_angle)))
                    
                    response_data = json.dumps({"message": "Servos bewegt", "x": x_angle, "y": y_angle, "z": z_angle})
            else:
               

                    response_data = """\
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Greifarm Steuerung</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            text-align: center;
            width: 300px;
        }
        .header {
            background-color: #e0e0e0;
            padding: 10px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }
        h1 {
            color: #333;
        }
        label {
            display: block;
            margin: 10px 0 5px;
            color: #555;
        }
        input[type="number"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #007bff;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        button:hover:enabled {
            background-color: #0056b3;
        }
        .control-panel {
            background-color: #e0e0e0;
            padding: 10px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .arrow-buttons {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }
        .arrow-buttons div {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .arrow-buttons button {
            margin: 5px;
            width: 40px;
            height: 40px;
            font-size: 18px;
            line-height: 18px;
            padding: 0;
        }
    </style>
    <script>
        function sendServoData() {
            let x = document.getElementById("xInput").value;
            let y = document.getElementById("yInput").value;
            let z = document.getElementById("zInput").value;
            x = Math.max(90, Math.min(270, x));
            y = Math.max(90, Math.min(270, y));
            z = Math.max(90, Math.min(270, z));
            fetch("/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ "x": x, "y": y, "z": z })
            }).then(response => response.json())
              .then(json => console.log(json));

            // Disable the send button for 5 seconds
            let sendButton = document.getElementById("sendButton");
            sendButton.disabled = true;
            setTimeout(() => {
                sendButton.disabled = false;
            }, 5000);
        }
        function moveServo(axis, direction) {
            let input = document.getElementById(axis + "Input");
            let value = parseInt(input.value);
            value += direction;
            if (value > 270) value = 270;
            if (value < 0) value = 0;
            input.value = value;
            sendServoData();
        }
        function toggleMagnet() {
            let magnetState = document.getElementById("magnetButton").innerText === "Magnet Aktivieren";
            fetch("/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ "magnet": magnetState })
            }).then(response => response.json())
              .then(json => {
                  console.log(json);
                  document.getElementById("magnetButton").innerText = magnetState ? "Magnet Deaktivieren" : "Magnet Aktivieren";
              });
        }
        function shutdownServer() {
            fetch("/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ "shutdown": true })
            }).then(response => response.json())
              .then(json => console.log(json));
        }
        function validateInput(input) {
            if (input.value > 270) {
                input.value = 270;
            }
            if (input.value < 0) {
                input.value = 0;
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <button onclick="shutdownServer()">Server Herunterfahren</button>
        </div>
        <h1>Greifarm Steuerung</h1>
        <label>X:</label> <input type="number" id="xInput" min="0" max="270" value="90" oninput="validateInput(this)"><br>
        <label>Y:</label> <input type="number" id="yInput" min="0" max="270" value="90" oninput="validateInput(this)"><br>
        <label>Z:</label> <input type="number" id="zInput" min="0" max="270" value="90" oninput="validateInput(this)"><br>
        <button onclick="sendServoData()" id="sendButton">Send</button>
        <br><br>
        <button onclick="toggleMagnet()" id="magnetButton">Magnet Aktivieren</button>
        <br> <br>
        <div class="control-panel">
            <div class="arrow-buttons">
                <div>
                    <label>Y-Achse</label>
                    <button onclick="moveServo('y', 10)">&#9650;</button>
                    <button onclick="moveServo('y', -10)">&#9660;</button>
                </div>
                <div style="margin-left: 20px;">
                    <label>X-Achse</label>
                    <button onclick="moveServo('x', -10)">&#9668;</button>
                    <button onclick="moveServo('x', 10)">&#9658;</button>
                </div>
                <div style="margin-left: 20px;">
                    <label>Z-Achse</label>
                    <button onclick="moveServo('z', 10)">&#9650;</button>
                    <button onclick="moveServo('z', -10)">&#9660;</button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>

"""         
            cl.send(response_data.encode('utf-8'))
            cl.close()
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        s.close()
        print("Server wurde heruntergefahren")

# Start the server 
wlanConnectundServer()





