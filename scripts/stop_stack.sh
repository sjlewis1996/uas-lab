#!/bin/bash

echo "Stopping UAS Lab..."

pkill -f sim_vehicle.py
pkill -f fgfs
pkill -f QGroundControl
pkill -f flight_log_summary.py
pkill -f battery_return_monitor.py

echo "All UAS processes stopped."

