# UAS Lab

ArduPilot + FlightGear + QGroundControl autonomous UAS development environment.

## Features

- ArduPilot SITL simulation
- FlightGear visual simulation
- QGroundControl integration
- MAVLink telemetry tools
- Flight log analysis
- Custom launch locations
- Dockerized Python tooling
- Experimental camera control scripts

---

# Quick Start

## Clone Repository

```bash
git clone https://github.com/sjlewis1996/uas-lab.git
cd uas-lab
```

---

# Initial Setup

Run the installer:

```bash
chmod +x setup/install_uas_lab.sh
./setup/install_uas_lab.sh
```

Then reload bash:

```bash
source ~/.bashrc
```

---

# Launch Commands

## Standard Launch

```bash
simplane
```

## Trial Field Launch

```bash
simplane_home
```

---

# Custom Locations

## KLZU Runway 7

```text
KLZU_RWY7=33.974738,-83.970493,324,64
```

## Trial Field

```text
TRIAL_FIELD=33.968638,-84.415519,327,6
```

---

# Scripts

## Flight Log Summary

```bash
python3 scripts/flight_log_summary.py
```

## Camera Utilities

```bash
python3 scripts/fg_camera_center.py
python3 scripts/fg_camera_test.py
```

---

# Docker

## Build

```bash
docker compose -f docker/docker-compose.yml build
```

## Run FlightLog Container

```bash
docker compose -f docker/docker-compose.yml run --rm flightlog
```

---

# Current Aircraft Plans

## Proof of Concept
- X-UAV Mini Talon

## Long-Term Platform
- RMRC Anaconda

---

# Future Goals

- Autonomous battery-aware RTL
- Real gimbal integration
- Companion computer architecture
- LTE telemetry
- AI-assisted mission planning
- Automated flight analysis
