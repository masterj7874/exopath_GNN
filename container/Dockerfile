FROM python:3.12.10-slim

WORKDIR /opt/exopath-gnn
COPY . .
ENV PYTHONPATH=/opt/exopath-gnn/src

CMD ["python", "scripts/run_protocol_demo.py", "--output", "/tmp/exopath-demo"]

