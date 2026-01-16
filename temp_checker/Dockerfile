FROM python:3.14-alpine

WORKDIR /app

RUN adduser -D -g '' appuser && \
	apk add --no-cache curl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

USER appuser

EXPOSE 8013

CMD ["python", "main.py"]
