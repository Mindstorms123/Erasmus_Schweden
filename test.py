// test for the client liberary

from clientlib import GreifarmClient
client = GreifarmClient("Put IP Address here")

response=client.send_servo_position(x=120, y=150, z=200) // Werte von 0 bis 270
print("Servo response", response)

response2 = client.toggle_magnet(TRUE) // TRUE oder FALSE
print("Magnet response", response2)

response3 = client.shutdown_server()
print("Server shutdown")
