# Dockerfile
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add wait-for-it script
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD ["bash", "-c", "./wait-for-it.sh db:5432 -- python manage.py makemigrations && python manage.py migrate && python manage.py ingest_data && python manage.py runserver 0.0.0.0:8000"]
