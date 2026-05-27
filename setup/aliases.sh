# UAS Lab Aliases

alias simplane='
fgfs --native-fdm=socket,in,30,,5503,udp --fdm=external --aircraft=ufo --airport=KLZU >/dev/null 2>&1 &

sleep 10

~/Downloads/QGroundControl-x86_64.AppImage &

sleep 5

cd ~/ardupilot/ArduPlane && \
python3 ~/uas-lab/scripts/flight_log_summary.py &

cd ~/ardupilot/ArduPlane && \
python3 ../Tools/autotest/sim_vehicle.py \
-v ArduPlane \
-L KLZU_RWY7 \
--enable-fgview \
--out=udp:127.0.0.1:14551
'

alias flightlog="cd ~/uas-lab/scripts && python3 flight_log_summary.py"

alias simplane_home='
fgfs --native-fdm=socket,in,30,,5503,udp --fdm=external --aircraft=ufo --lat=33.968638 --lon=-84.415519 --altitude=1073 --heading=6 >/dev/null 2>&1 &

sleep 10

~/Downloads/QGroundControl-x86_64.AppImage &

sleep 5

cd ~/ardupilot/ArduPlane && \
python3 ~/uas-lab/scripts/flight_log_summary.py &

cd ~/ardupilot/ArduPlane && \
python3 ../Tools/autotest/sim_vehicle.py \
-v ArduPlane \
-L TRIAL_FIELD \
--enable-fgview \
--out=udp:127.0.0.1:14551
'
