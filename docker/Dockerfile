FROM python:3.12-slim

WORKDIR /uas-lab

RUN pip install --no-cache-dir pymavlink pandas matplotlib

COPY scripts/ ./scripts/

CMD ["python3", "scripts/flight_log_summary.py"]

