FROM python:3.14-alpine

RUN pip install --no-cache-dir python-dotenv

WORKDIR /app
COPY app/temp_exporter.py .

VOLUME ["/sys/class/thermal"]

EXPOSE 8080

RUN adduser -D -g '' thermaluser
USER thermaluser

CMD ["python", "temp_exporter.py"]
