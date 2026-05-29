#!/usr/bin/env python3

from pymavlink import mavutil
import time
import math

MAVLINK_PORT = "udpin:127.0.0.1:14552"

MIN_GROUNDSPEED_MPS = 12.0
RETURN_RESERVE_SEC = 120
CAUTION_BUFFER_SEC = 120

ABS_CAUTION_PCT = 35
ABS_RETURN_PCT = 25

home_lat = home_lon = None
lat = lon = None
groundspeed = None
battery_pct = None
last_batt_update = 0
last_status = "UNKNOWN"
battery_history = []


def distance_m(lat1, lon1, lat2, lon2):
    r = 6371000
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def burn_rate_pct_per_sec():
    if len(battery_history) < 2:
        return None

    old_t, old_pct = battery_history[0]
    new_t, new_pct = battery_history[-1]

    dt = new_t - old_t
    burn = old_pct - new_pct

    if dt <= 0 or burn <= 0:
        return None

    return burn / dt


print("Battery return monitor started.")

master = mavutil.mavlink_connection(MAVLINK_PORT)

while True:
    msg = master.recv_match(blocking=True, timeout=1)

    if msg is None:
        continue

    msg_type = msg.get_type()

    if msg_type == "GLOBAL_POSITION_INT":
        lat = msg.lat / 1e7
        lon = msg.lon / 1e7

        # cm/s to m/s
        groundspeed = math.sqrt(msg.vx**2 + msg.vy**2) / 100.0

    elif msg_type == "HOME_POSITION":
        home_lat = msg.latitude / 1e7
        home_lon = msg.longitude / 1e7

    elif msg_type == "SYS_STATUS":
        if msg.battery_remaining >= 0:
            battery_pct = float(msg.battery_remaining)
            last_batt_update = time.time()
            battery_history.append((last_batt_update, battery_pct))

            # Keep 10 minutes of battery history
            battery_history = [
                x for x in battery_history if last_batt_update - x[0] <= 600
            ]

    if None in (lat, lon, home_lat, home_lon, battery_pct):
        continue

    # Ignore stale battery data
    if time.time() - last_batt_update > 5:
        continue

    dist_home = distance_m(lat, lon, home_lat, home_lon)

    effective_speed = max(groundspeed or 0, MIN_GROUNDSPEED_MPS)
    time_to_home_sec = dist_home / effective_speed

    burn_rate = burn_rate_pct_per_sec()

    if burn_rate:
        time_remaining_sec = battery_pct / burn_rate
    else:
        time_remaining_sec = None

    required_sec = time_to_home_sec + RETURN_RESERVE_SEC
    caution_sec = required_sec + CAUTION_BUFFER_SEC

    status = "SAFE"

    if battery_pct <= ABS_RETURN_PCT:
        status = "RETURN NOW"
    elif battery_pct <= ABS_CAUTION_PCT:
        status = "CAUTION"

    if time_remaining_sec is not None:
        if time_remaining_sec <= required_sec:
            status = "RETURN NOW"
        elif time_remaining_sec <= caution_sec:
            status = "CAUTION"

    if status != last_status:
        if status == "CAUTION":
            if time_remaining_sec:
                eta_return_now = max(0, time_remaining_sec - required_sec) / 60
                print(
                    f"BATTERY STATUS: CAUTION | "
                    f"Battery: {battery_pct:.0f}% | "
                    f"Distance home: {dist_home:.0f} m | "
                    f"Time home: {time_to_home_sec/60:.1f} min | "
                    f"Estimated RETURN NOW in {eta_return_now:.1f} min"
                )
            else:
                print(
                    f"BATTERY STATUS: CAUTION | "
                    f"Battery: {battery_pct:.0f}% | "
                    f"Distance home: {dist_home:.0f} m"
                )

        elif status == "RETURN NOW":
            print(
                f"BATTERY STATUS: RETURN NOW | "
                f"Battery: {battery_pct:.0f}% | "
                f"Distance home: {dist_home:.0f} m | "
                f"Time home: {time_to_home_sec/60:.1f} min"
            )

        elif status == "SAFE" and last_status != "UNKNOWN":
            print(f"BATTERY STATUS: SAFE | Battery: {battery_pct:.0f}%")

        last_status = status

    time.sleep(1)

