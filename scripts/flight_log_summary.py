from pymavlink import mavutil
import time
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

OUT_DIR = Path.home() / "uas_lab" / "reports"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print("Connecting to MAVLink on udp:127.0.0.1:14551...")
master = mavutil.mavlink_connection("udp:127.0.0.1:14551")
master.wait_heartbeat()
print("Connected. Waiting for flight data...")

start_time = time.time()
was_armed = False

samples = []
mode_changes = []
warnings = []
waypoints = []

last_mode = None
last_wp =  None

def is_armed(msg):
	return bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)

def get_mode(msg):
	return mavutil.mode_string_v10(msg)

while True:
	msg = master.recv_match(blocking=True, timeout=1)
	if msg is None:
		continue
	
	now = time.time() - start_time
	mtype = msg.get_type()

	if mtype == "HEARTBEAT":
		armed = is_armed(msg)
		mode = get_mode(msg)

		if mode != last_mode:
			mode_changes.append((now, mode))
			last_mode = mode

		if was_armed and not armed:
			print("\nDISARM DETECTED - generating post-flight summary...\n")
			break

		was_armed =  armed

	elif mtype == "VFR_HUD":
		samples.append({
			"time": now,
			"altitude_m": msg.alt,
			"airspeed_mps": msg.groundspeed,
			"climb_mps": msg.climb,
			"battery_v": None,
			"battery_a": None,
			"gps_fix": None,
			"satellites": None
		})

	elif mtype == "SYS_STATUS" and samples:
		samples[-1]["battery_v"] = msg.voltage_battery / 1000.0
		samples[-1]["battery_a"] = msg.current_battery / 100.0 if msg.current_battery != -1 else None
	
	elif mtype == "GPS_RAW_INT" and samples:
		samples[-1]["gps_fix"] = msg.fix_type
		samples[-1]["satellites"] = msg.satellites_visible

	elif mtype == "MISSION_CURRENT":
		if msg.seq != last_wp:
			waypoints.append((now, msg.seq))
			last_wp = msg.seq

	elif mtype == "STATUSTEXT":
		warnings.append((now, msg.severity, msg.text))

df = pd.DataFrame(samples)

if df.empty:
	print("No usable telemetry samples collected.")
	exit()

duration = df["time"].max()
max_alt = df["altitude_m"].max()
min_alt = df["altitude_m"].min()
max_airspeed = df["airspeed_mps"].max()
avg_airspeed = df["airspeed_mps"].mean()

valid_batt = df["battery_v"].dropna()
valid_batt = valid_batt[valid_batt > 0]

valid_sats = df["satellites"].dropna()
valid_sats = valid_sats[valid_sats > 0]

valid_fix = df["gps_fix"].dropna()
valid_fix = valid_fix[valid_fix > 0]

min_batt = valid_batt.min() if not valid_batt.empty else None

max_climb = df["climb_mps"].max()
max_descent = df["climb_mps"].min()

landing_phase = df.tail(30)
landing_descent_avg = landing_phase["climb_mps"].mean()
landing_airspeed_avg = landing_phase["airspeed_mps"].mean()

print("========== Flight Log Summary ==========")
print(f"Mission duration: {duration:1f} sec")
print(f"Altitude range: {min_alt:.1f} m to {max_alt:.1f} m")
print(f"Max airspeed: {max_airspeed:.1f} m/s")
print(f"Avg airspeed: {avg_airspeed:.1f} m/s")
print(f"Max climb rate: {max_climb:.1f} m/s")
print(f"Max descent rate: {max_descent:.1f} m/s")

if min_batt is not None:
	print(f"Minimum battery voltage: {min_batt:.2f} V")
else:
	print("Minimum battery voltage: No valid battery data")

print("\nFlight mode changes:")
for t, mode in mode_changes:
	print(f"  {t:7.1f}s  {mode}")

print("\nWaypoint progress:")
for t, wp in waypoints:
	print(f"  {t:7.1f}s Waypoint {wp}")

print("\nGPS quality:")
if not valid_sats.empty:
	print(f"  Satellites min/max: {valid_sats.min():.0f} / {valid_sats.max():.0f}")
else:
	print("  Satellites: No valid satellite data")

if not valid_fix.empty:
	print(f"  GPS fix min/max: {valid_fix.min():.0f} / {valid_fix.max():.0f}")
else:
	print("  GPS fix: No valid GPS fix data")


print("\nLanding approach stability:")
print(f"  Final avg descent rate: {landing_descent_avg:.2f} m/s")
print(f"  Final avg airspeed: {landing_airspeed_avg:.2f} m/s")

print("\nWarnings / events:")
if warnings:
	for t, sev, text in warnings:
		print(f"  {t:7.1f}s  Severity {sev}: {text}")
else:
	print("  No warnings events captured.")

timestamp = int(time.time())

plots = [
	("altitude_m", "Altitude vs Time", "Altitude (m)"),
	("airspeed_mps", "Airspeed vs Time", "Airspeed (m/s)"),
	("battery_v", "Battery Voltage vs Time", "Voltage (V)"),
	("battery_a", "Battery Current vs Time", "Current (A)"),
	("climb_mps", "Climb / Descent Rate vs Time", "Climb Rate (m/s)")
]

for column, title, ylabel in plots:
	if column in df.columns and df[column].notna().any():
		plt.figure()
		plt.plot(df["time"], df[column])
		plt.title(title)
		plt.xlabel("Time (sec)")
		plt.ylabel(ylabel)
		plt.grid(True)
		plt.savefig(OUT_DIR / f"{timestamp}_{column}.png")
		plt.close()

csv_path = OUT_DIR / f"{timestamp}_flight_data.csv"
df.to_csv(csv_path, index=False)

print(f"\nSaved CSV and plots to: {OUT_DIR}")
print("========================================")

