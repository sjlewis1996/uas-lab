import socket
import time

FG_HOST = "127.0.0.1"
FG_PORT = 5400

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((FG_HOST, FG_PORT))

def send(cmd):
	sock.send((cmd + "\r\n").encode())
	time.sleep(0.1)

send("set /sim/current-view/viewnumber 0")
send("set /sim/current-view/heading-offset-deg 0")
send("set /sim/current-view/pitch-offset-deg 0")
send("set /sim/current-view/roll-offset-deg 0")

print("Camera command send to FlightGear.")

sock.close()
