#!/bin/bash

echo "Starting UAS Lab..."

# Start FlightGear
fgfs --native-fdm=socket,in,30,,5503,udp \
  --fdm=external \
  --aircraft=ufo \
  --lat=33.968638 \
  --lon=-84.415519 \
  --altitude=1073 \
  --heading=6 \
  --telnet=5400 \
  >/dev/null 2>&1 &

sleep 10

# Start QGroundControl
~/Downloads/QGroundControl-x86_64.AppImage &

sleep 5

# Start FlightLog
cd ~/ardupilot/ArduPlane || exit
python3 ~/uas-lab/scripts/flight_log_summary.py &

# Start ArduPlane SITL
python3 ../Tools/autotest/sim_vehicle.py \
  -v ArduPlane \
  -L TRIAL_FIELD \
  --enable-fgview \
  --out=udp:127.0.0.1:14551

