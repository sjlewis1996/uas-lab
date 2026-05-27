import socket
import time
import math
import sys

FG_HOST = "127.0.0.1"
FG_PORT = 5400

if len(sys.argv) != 4:
    print("Usage: python3 fg_camera_track.py TARGET_LAT TARGET_LON TARGET_ALT_M")
    sys.exit(1)
TARGET_LAT = float(sys.argv[1])
TARGET_LON = float(sys.argv[2])
TARGET_ALT_M = float(sys.argv[3])

def connect_fg():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((FG_HOST, FG_PORT))
    return sock

def send(sock, cmd):
    sock.send((cmd + "\r\n").encode())
    time.sleep(0.05)

def get(sock, prop):
    sock.send((f"get {prop}\r\n").encode())
    time.sleep(0.1)
    data = sock.recv(4096).decode(errors="ignore")

    for line in data.splitlines():
        if "=" in line:
            value = line.split("=", 1)[1].strip()
            value = value.split()[0].strip("'\"")
            try:
                return float(value)
            except ValueError:
                return None

    return None

def bearing_deg(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    return (math.degrees(math.atan2(y, x)) + 360) % 360

def distance_m(lat1, lon1, lat2, lon2):
    r = 6371000
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    dlat = lat2 - lat1
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

sock = connect_fg()

print("Camera tracking started. Press CTRL+C to stop.")

try:
    send(sock, "set /sim/current-view/view-number 0")

    while True:
        lat = get(sock, "/position/latitude-deg")
        lon = get(sock, "/position/longitude-deg")
        alt_ft = get(sock, "/position/altitude-ft")
        heading = get(sock, "/orientation/heading-deg")

        if None in (lat, lon, alt_ft, heading):
            print("Waiting for FlightGear position data...")
            time.sleep(1)
            continue

        alt_m = alt_ft * 0.3048
        target_bearing = bearing_deg(lat, lon, TARGET_LAT, TARGET_LON)
        horizontal_dist = distance_m(lat, lon, TARGET_LAT, TARGET_LON)
        vertical_diff = TARGET_ALT_M - alt_m

        pitch = -math.degrees(math.atan2(vertical_diff, horizontal_dist))
        yaw_offset = ((target_bearing - heading + 540) % 360) - 180
        yaw_offset = max(min(yaw_offset, 120), -120)

        send(sock, f"set /sim/current-view/heading-offset-deg {yaw_offset:.2f}")
        send(sock, f"set /sim/current-view/pitch-offset-deg {pitch:.2f}")

        print(f"Cam yaw offset: {yaw_offset:.1f} deg | pitch: {pitch:.1f} deg")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nCamera tracking stopped.")

finally:
    sock.close()
