FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser && \
    mkdir -p /home/appuser/.ssh && \
    chown -R appuser:appuser /home/appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/
COPY ssh/ /home/appuser/.ssh/

RUN chmod 600 /home/appuser/.ssh/id_ed25519 && \
    echo "Host 192.168.88.80\n    StrictHostKeyChecking no" > /home/appuser/.ssh/config && \
    chown -R appuser:appuser /home/appuser/.ssh

USER appuser

EXPOSE 8013

CMD ["python", "main.py"]
