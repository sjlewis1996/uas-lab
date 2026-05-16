# UAS Lab Aliases

alias simplane="~/Downloads/QGroundControl-x86_64.AppImage & cd ~/ardupilot/ArduPlane && python3 ~/uas-lab/scripts/flight_log_summary.py & cd ~/ardupilot/ArduPlane && python3 ../Tools/autotest/sim_vehicle.py -v ArduPlane --out=udp:127.0.0.1:14551"

alias flightlog="cd ~/uas-lab/scripts && python3 flight_log_summary.py"
