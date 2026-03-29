FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
# Dépendances système
RUN apt-get update && apt-get install -y gcc libpq-dev

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt


COPY . .
RUN mkdir -p staticfiles media
RUN python manage.py collectstatic --noinput
EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py createsuperuser --noinput || true && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]