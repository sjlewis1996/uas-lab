#!/bin/bash

echo "Stopping UAS Lab..."

pkill -f sim_vehicle.py
pkill -f fgfs
pkill -f QGroundControl
pkill -f flight_log_summary.py

echo "All UAS processes stopped."

